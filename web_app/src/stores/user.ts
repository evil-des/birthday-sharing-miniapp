import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface UserState {
  id: number | null;
  chatID: number | null;
  firstName: string | null;
  lastName: string | null;
  username: string | null;
  birthday: Date | null;
  photoURL: string | null;
  dateStarted: Date | null;
  shareLink: string | null;
}

export const useUserStore = defineStore('userStore', () => {
  // State
  const userData = ref<UserState | null>(null);

  const setUserData = (data: UserState) => {
    userData.value = data;
  };

  return { setUserData, userData };
});