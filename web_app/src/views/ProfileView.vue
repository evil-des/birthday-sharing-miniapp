<template>
  <div class="flex h-full flex-col pb-10">
    <div class="h-full flex flex-col text-center">
      <div class="flex justify-center py-10">
        <img v-bind:hidden="!userData?.photoURL" :src="userData?.photoURL" width="80" height="80" class="rounded-full">
      </div>
      <div class="flex flex-col justify-center">
        <p class="text-2xl">{{ userData?.firstName }} {{ userData?.lastName }}</p>
        <a :href="userLink" class="text-lg">@{{ userData?.username }}</a>
      </div>

      <!-- <div v-if="dateStore.timeDiff.days === 0" class="flex flex-col pt-24 justify-center text-center">
        <p class="text-4xl">С днем рождения! 🎉</p>
      </div> -->

      <div class="flex flex-col pt-24 justify-center text-center">
        <p class="text-4xl">До дня рождения</p>
        <p class="pt-5 text-2xl font-bold">{{ countBirthday }}</p>
      </div>
    </div>

    <div class="button" @click="onShareClick">Поделиться</div>
  </div>
</template>


<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useDateStore } from '@/stores/date';
import { computed, inject, onMounted, ref } from 'vue';
import type { ComputedRef } from 'vue';
import type { TelegramWebApp } from '@longpoll/telegram-webapp-types';
import { useUserStore } from '@/stores/user';
import type ApiService from '@/services/api';
import type { ITimeDiff } from '@/stores/date';

const router = useRouter();
const dateStore = useDateStore(); 
const userStore = useUserStore();

const userData = computed(() => userStore.userData);
const apiService = inject<ApiService>('apiService');

const countBirthday: ComputedRef<string> = computed(() => dateStore.countBirthday);
const timeDiff: ComputedRef<ITimeDiff> = computed(() => dateStore.timeDiff);
const userLink: ComputedRef<string> = computed(() => `https://t.me/${userData.value?.username}`);

let WebApp: TelegramWebApp.WebApp | null = null;

onMounted(() => {
  WebApp = window?.Telegram?.WebApp;

  if (WebApp) {
    if (dateStore.selectedDate && userData?.value.id) {
      apiService?.setBirthday(userData?.value.id, dateStore.selectedDate)
    }
    
    if (!WebApp.initDataUnsafe.start_param) {
      WebApp.BackButton.onClick(() => router.push({path: "/"}));
      WebApp.BackButton.show();
    }
  }
})


function onShareClick() {
  const shareText = "Смотри сколько осталось до моего дня рождения!"
  WebApp?.openTelegramLink(`https://t.me/share/url?url=${userData.value?.shareLink}&text=${shareText}`)
}

</script>