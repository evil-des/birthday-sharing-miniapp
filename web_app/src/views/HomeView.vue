<template>
  <DatePicker @dateSelected="updateDate"/>
  <div class="button" @click="onNextClick">Продолжить</div>
</template>


<script setup lang="ts">
import DatePicker from '@/components/DatePicker.vue'
import { useDateStore } from '@/stores/date' // Import the Pinia store
import { useRouter } from 'vue-router'
import { computed, onMounted } from 'vue'
import type { TelegramWebApp } from '@longpoll/telegram-webapp-types';

const dateStore = useDateStore(); // Initialize the Pinia store
const router = useRouter();

let WebApp: TelegramWebApp.WebApp | null = null;

function onNextClick() {
  router.push({path: "/profile"})
}

function updateDate(date: Date) {
  dateStore.setSelectedDate(date); // Update the store with the selected date
  console.log(computed(() => dateStore.formattedDate))
};

onMounted(() => {
  WebApp = window?.Telegram?.WebApp;

  if (WebApp?.BackButton.isVisible) {
    WebApp.BackButton.hide()
  }
})

</script>