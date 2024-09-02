import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface DateStoreState {
  selectedDay: number | null;
  selectedMonth: number | null;
  selectedYear: number | null;
  selectedDate: Date | null;
  months: string[];
}

export interface ITimeDiff {
  days: number, 
  hours: number, 
  minutes: number
}

export const useDateStore = defineStore('dateStore', () => {
  // State
  const selectedDay = ref<number | null>(null);
  const selectedMonth = ref<number | null>(null);
  const selectedYear = ref<number | null>(null);
  const selectedDate = ref<Date | null>(null);

  const timeDiff = ref<ITimeDiff>({
    days: 0,
    hours: 0,
    minutes: 0
  });

  const months = ref<string[]>([
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 
    'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ]);

  // Getters
  const formattedDate = computed<string | null>(() => {
    if (selectedDate.value !== null) {
      return selectedDate.value.toLocaleDateString('ru-RU', {
        // weekday: 'long', // "Monday"
        year: 'numeric', // "2023"
        month: 'long', // "August"
        day: 'numeric' // "31"
      });;
    }
    return null;
  });

  const countBirthday = computed<string>(() => {
    if (selectedDate.value !== null) {
      const birthDay = new Date(selectedDate.value);
      birthDay.setFullYear(new Date().getFullYear())

      let diff = timeBetween(new Date(), birthDay);

      // if birthday has already been in this year
      if (diff.days < 0) { 
        birthDay.setFullYear(new Date().getFullYear() + 1)
        diff = timeBetween(new Date(), birthDay)
      }

      return `${diff.days} дней, ${diff.hours} часов, ${diff.minutes} минут`;
    }
    return "";
  });

  const timeBetween = (startDate: Date, endDate: Date): ITimeDiff => {
    if (!(startDate instanceof Date) || !(endDate instanceof Date)) {
      throw new Error('Apply correct objects of type Date.');
    }
    
    // Calculate the difference in milliseconds
    const diffTime = endDate.getTime() - startDate.getTime();
    
    // Calculate days, hours, and minutes
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor((diffTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffTime % (1000 * 60 * 60)) / (1000 * 60));

    timeDiff.value = {
      days: diffDays,
      hours: diffHours,
      minutes: diffMinutes,
    }

    return timeDiff.value;
  }

  // Actions
  const setDay = (day: number) => {
    selectedDay.value = day;
  };

  const setMonth = (monthIndex: number) => {
    selectedMonth.value = monthIndex;
  };

  const setYear = (year: number) => {
    selectedYear.value = year;
  };

  const setSelectedDate = (date: Date) => {
    selectedDate.value = date;
  };

  const resetDate = () => {
    selectedDay.value = null;
    selectedMonth.value = null;
    selectedYear.value = null;
  };

  return {
    // State
    selectedDay,
    selectedMonth,
    selectedYear,
    selectedDate,
    months,
    timeDiff,
    // Getters
    formattedDate,
    countBirthday,
    // Actions
    setDay,
    setMonth,
    setYear,
    setSelectedDate,
    resetDate,
  };
});