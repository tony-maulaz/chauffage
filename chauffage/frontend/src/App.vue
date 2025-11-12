<script setup>
import { onMounted } from "vue";
import Dashboard from "@/views/Dashboard.vue";

onMounted(() => {
  document.title = "Home";
});
</script>

<template>
  <Dashboard />
</template>
