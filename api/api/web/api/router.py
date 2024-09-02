from fastapi.routing import APIRouter
# from fastapi import Depends
# from api.web.auth_bearer import JWTBearer
# from api.web.api import CustomRouter
from api.web.api import monitoring, redis, user


# , dependencies=[Depends(JWTBearer())]

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
