<template>
    <div class="datepicker">
        <!-- Day Picker -->
        <div class="picker" @scroll="onScroll('day')" ref="dayPicker">
            <ul class="list">
                <li
                v-for="day in days"
                :key="day"
                :class="{ selected: selectedDay === day }"
                >
                {{ day }}
                </li>
            </ul>
        </div>

        <!-- Month Picker -->
        <div class="picker" @scroll="onScroll('month')" ref="monthPicker">
            <ul class="list">
                <li
                v-for="(month, index) in months"
                :key="index"
                :class="{ selected: selectedMonth === index }"
                >
                {{ month }}
                </li>
            </ul>
        </div>

        <!-- Year Picker -->
        <div class="picker" @scroll="onScroll('year')" ref="yearPicker">
            <ul class="list">
                <li
                v-for="year in years"
                :key="year"
                :class="{ selected: selectedYear === year }"
                >
                {{ year }}
                </li>
            </ul>
        </div>

        <!-- Central Selection Zone Overlay -->
        <div class="selection-zone"></div>
    </div>
</template>
  
<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import type { Ref } from 'vue';
import { useDateStore } from '@/stores/date'

interface ScrollTimeouts {
    day: number | null;
    month: number | null;
    year: number | null;
}

const dateStore = useDateStore();
const selectedDate = dateStore.selectedDate;

const selectedDay = ref<number>(0);
const selectedMonth = ref<number>(0); // January (months are 0-based in JavaScript)
const selectedYear = ref<number>(new Date().getFullYear()); // Default to the current year

// Computed lists for days, months, and years
const days = computed<number[]>(() => Array.from({ length: 31 }, (_, i) => i + 1)); // 1 to 31
const months = ref<string[]>([
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 
    'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
]);
const years = computed<number[]>(() => Array.from({ length: new Date().getFullYear() - 1930 + 1 }, (_, i) => i + 1930)); // 1930 to current year

// Refs for scrollable containers
const dayPicker = ref<HTMLElement | null>(null);
const monthPicker = ref<HTMLElement | null>(null);
const yearPicker = ref<HTMLElement | null>(null);
const scrollTimeouts: ScrollTimeouts = {
    day: null,
    month: null,
    year: null,
};

let lastHapticTime = 0;
const HAPTIC_INTERVAL = 1000;

// Adjust the scroll position to center the item in the selection zone
function onScroll(type: "day" | "month" | "year") {
    if (scrollTimeouts[type] !== null) {
        clearTimeout(scrollTimeouts[type]!);
    }

    scrollTimeouts[type] = setTimeout(() => {
        const pickerRef: Ref<HTMLElement | null> = type === 'day' ? dayPicker : type === 'month' ? monthPicker : yearPicker;
        if (pickerRef.value) {
            const picker = pickerRef.value;
            const listItems = picker.querySelectorAll<HTMLElement>('.list li');
            const pickerCenter = picker.clientHeight / 2; // Center of the picker

            let closestItem: HTMLElement | null = null;
            let closestDistance = Infinity;

            listItems.forEach((item: HTMLElement) => {
                const itemCenter = item.offsetTop + item.clientHeight / 2 - picker.scrollTop;
                const distance = Math.abs(pickerCenter - itemCenter);
                if (distance < closestDistance) {
                    closestDistance = distance;
                    closestItem = item;
                }
            });

            if (closestItem) {
                const value = (closestItem as HTMLElement).innerText;
                if (type === 'day') {
                    selectedDay.value = parseInt(value, 10);
                } else if (type === 'month') {
                    selectedMonth.value = months.value.indexOf(value);
                } else {
                    selectedYear.value = parseInt(value, 10);
                }

                nextTick(() => {
                    picker.scrollTo({
                        top: closestItem!.offsetTop - picker.clientHeight / 2 + closestItem!.clientHeight / 2,
                        behavior: 'smooth',
                    });

                    const now = Date.now();
                    
                    // Send HapticFeedback to the user when the date selected
                    if (window?.Telegram?.WebApp && now - lastHapticTime > HAPTIC_INTERVAL) {
                        window.Telegram.WebApp.HapticFeedback.selectionChanged();
                        lastHapticTime = now;
                    }
                });
            }
        }
    }, 100); // Debounce to allow smooth scroll
}

// Log changes whenever a date part is selected
watch([selectedDay, selectedMonth, selectedYear], emitDate);

const emit = defineEmits(['dateSelected']);

function emitDate() {
  emit('dateSelected', new Date(selectedYear.value, selectedMonth.value, selectedDay.value));
};

async function setDefaultDate() {
    await nextTick();

    ["day", "month", "year"].forEach((type) => {
        const pickerRef: Ref<HTMLElement | null> = type === 'day' ? dayPicker : type === 'month' ? monthPicker : yearPicker;
        
        if (pickerRef.value) {
            const picker = pickerRef.value;
            const listItems = picker.querySelectorAll<HTMLElement>('.list li');

            let item, defaultDate;

            // If user returns to main page, the selected date remains
            if (selectedDate !== null) {
                defaultDate = selectedDate;
            } else {
                defaultDate = new Date();
            }

            if (type === "day") {
                item = listItems[defaultDate.getDate() - 1]
            } else if (type === "month") {
                item = listItems[defaultDate.getMonth()]
            } else {
                item = listItems[listItems.length - 1];
            }
            
            picker.scrollTo({
                top: item.offsetTop - picker.clientHeight / 2 + item.clientHeight / 2,
                behavior: 'smooth',
            });
        }
    })
}

onMounted(setDefaultDate);

</script>
  
<style scoped>
.datepicker {
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    color: #111111;
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    overflow: hidden;
    position: relative;
}

.picker {
    width: 80%;
    margin: 20px 0;
    max-height: 300px;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0;
    position: relative;
    scrollbar-width: thin;
    scrollbar-color: white rgba(255, 255, 255, 0.1);
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
    padding-top: 120px;
    padding-bottom: 120px; 

    /* Hide scrollbar for Chrome, Safari, and Opera */
    scrollbar-width: none; /* Hide scrollbar for Firefox */
    -ms-overflow-style: none;  /* Hide scrollbar for Internet Explorer and Edge */
}

.picker::-webkit-scrollbar {
    display: none; /* Hide scrollbar for Chrome, Safari, and Opera */
}

.list {
    list-style: none;
    padding: 0;
    margin: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.list li {
    text-align: center;
    padding: 15px 0;
    cursor: pointer;
    font-size: 1.2rem;
    color: #111111;
    width: 100%;
    transition: transform 0.2s, font-size 0.2s; /* Smooth transitions for magnification effect */
}

.list li.selected {
    font-size: 1.4rem;
    transform: scale(1.2);
    color: #ffb648;
}

.picker::-webkit-scrollbar {
    width: 8px;
}

.picker::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
}

.picker::-webkit-scrollbar-thumb {
    background-color: white;
    border-radius: 10px;
}

.selection-zone {
    position: absolute;
    top: 50%;
    left: 5%;
    right: 5%;
    height: 80px;
    margin-top: -40px;
    border-top: 2px solid rgba(153, 153, 153, 0.5);
    border-bottom: 2px solid rgba(153, 153, 153, 0.5);
    pointer-events: none;
    box-sizing: border-box;
}


@media (prefers-color-scheme: dark) {
  .datepicker {
    color: white;
  }

  .list li {
    color: white;
  }

  .list li.selected {
    color: #ffe0b2;
  }

  .selection-zone {
    border-top: 2px solid rgba(255, 255, 255, 0.5);
    border-bottom: 2px solid rgba(255, 255, 255, 0.5);
  }
}
</style>
  