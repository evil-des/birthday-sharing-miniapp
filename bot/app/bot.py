import asyncio

import aiojobs
import orjson
from aiocache import Cache
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiohttp import web
from redis.asyncio import Redis

from app import handlers, utils, web_handlers
from app.database.engine import AsyncSession
from app.utils.get_settings import get_settings


settings = get_settings()


async def create_db_connections(dp: Dispatcher) -> Cache:
    if settings.DEBUG:
        cache = Cache(cache_class=Cache.MEMORY)
    else:
        cache = Cache(
            cache_class=Cache.REDIS,
            endpoint=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_CACHE_DB,
        )

    return cache


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    if "session" in dp.workflow_data:
        session: AsyncSession = dp["session"]
        await session.close()
    if "cache" in dp.workflow_data:
        cache: Cache = dp["cache"]  # type: ignore[type-arg]
        await cache.REDIS.close()


def setup_handlers(dp: Dispatcher) -> None:
    dp.include_router(handlers.user.prepare_router())


async def setup_aiogram(dp: Dispatcher) -> None:
    await create_db_connections(dp)
    setup_handlers(dp)


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    await bot.set_webhook(
        url=settings.MAIN_WEBHOOK_ADDRESS.format(
            token=settings.BOT_TOKEN, bot_id=settings.BOT_TOKEN.split(":")[0]
        ),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=settings.MAIN_WEBHOOK_SECRET_TOKEN,
    )


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


def main() -> None:
    bot = Bot(settings.BOT_TOKEN, parse_mode="HTML")

    if settings.DEBUG:
        storage = MemoryStorage()
    else:
        storage = RedisStorage(
            redis=Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_STORAGE_DB,
            ),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
        # await redis.flushdb()

    dp = Dispatcher(storage=storage)

    if settings.USE_WEBHOOK:
        dp.startup.register(aiogram_on_startup_webhook)
        dp.shutdown.register(aiogram_on_shutdown_webhook)
        web.run_app(
            asyncio.run(setup_aiohttp_app(bot, dp)),
            handle_signals=True,
            host=settings.MAIN_WEBHOOK_LISTENING_HOST,
            port=settings.MAIN_WEBHOOK_LISTENING_PORT,
        )
    else:
        dp.startup.register(aiogram_on_startup_polling)
        dp.shutdown.register(aiogram_on_shutdown_polling)
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    main()
