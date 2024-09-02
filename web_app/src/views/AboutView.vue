<script setup lang="ts">
import DatePicker from '../components/DatePicker.vue'
</script>

<template>
  <div class="about">
    <DatePicker />
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>
