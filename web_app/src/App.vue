<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { onMounted, inject } from 'vue'
import type ApiService from '@/services/api';
import type { TelegramWebApp } from '@longpoll/telegram-webapp-types';
import { useUserStore } from './stores/user';
import { useDateStore } from '@/stores/date';
import type { IUser } from '@/services/api';

// Show active/focus state of elements on mobile phones
document.body.addEventListener('touchstart', function() {}, false);

const router = useRouter();
const dateStore = useDateStore(); 
const userStore = useUserStore();

const apiService = inject<ApiService>('apiService');
let WebApp: TelegramWebApp.WebApp | null = null;

if (window?.Telegram?.WebApp.initDataUnsafe.start_param) {
  router.push("/profile")
}

onMounted(() => {
  WebApp = window?.Telegram?.WebApp;

  apiService?.get("/health").
    then(response => {
      if (response.status == 200) {
        console.log(`Successfully connected to API Service! [${import.meta.env.VITE_API_URL}]`)
        const startParam = WebApp?.initDataUnsafe.start_param;

        if (WebApp?.initData && !startParam) {
          apiService?.validateInitData(WebApp.initData).
            then(response => {
              if (response?.data?.result) {
                setUserData(response.data)
              }
          })
          
        } else if (startParam) { // If User got invited to Mini App by link
          const userID = Number(atob(startParam))
          apiService.getUser({id: userID}).
            then(response => {
              if (response.data) {
                setUserData(response.data)

                if (response.data.birthday) {
                  dateStore.setSelectedDate(response.data.birthday)
                }

              } else {
                alert("Пользователь не найден!")
              }
          })
        }

      } else {
        throw Error(`Unsuccessfull attempt of connecting to API Service! [${import.meta.env.VITE_API_URL}]`)
      }
    })
})


const setUserData = (data: IUser) => {
  userStore.setUserData({
    id: data.id,
    chatID: data.chat_id,
    firstName: data.first_name,
    lastName: data.last_name,
    username: data.username,
    birthday: data.birthday,
    photoURL: data.photo_url,
    dateStarted: data.date_started,
    shareLink: data.share_link
  })
}
</script>

<template>
  <RouterView />
</template>
