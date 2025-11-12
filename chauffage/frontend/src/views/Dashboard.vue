<template>
  <v-app class="dashboard-app">
    <v-main>
      <div class="dashboard">
        <div v-if="DEBUG_MODE" class="dashboard__debug-banner">
          Mode debug actif — valeurs simulées (battery_low incluses)
        </div>
        <div class="dashboard__grid">
          <SensorCard
            v-for="card in orderedCards"
            :key="card.num"
            :name="card.name"
            :temperature="card.data?.temperature ?? null"
            :humidity="card.data?.humidity ?? null"
            :last-update="card.data?.last_update ?? null"
            :battery-low="card.data?.battery_low ?? false"
            :reachable="card.data?.reachable ?? true"
            :setpoint-temperature="card.data?.setpoint_temperature ?? null"
            :regulation-status="card.data?.regulation_status ?? null"
            :placeholder="card.placeholder"
          />
        </div>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import sensorsConfig from "@/config/sensors";
import { DEBUG_MODE, buildDebugSensors } from "@/config/debug";
import { APP_THEME_MODE } from "@/config/app";
import { fetchSensors } from "@/services/api";
import SensorCard from "@/components/SensorCard.vue";
import { useThemeController } from "@/composables/useThemeController";

const POLL_INTERVAL = Number(import.meta.env.VITE_POLL_INTERVAL || 60000);
const MAX_SLOTS = 12;

const sensors = ref([]);
const loading = ref(false);
const error = ref(null);
let intervalId;
let autoThemeInterval;

const { applyThemeMode } = useThemeController();

const applyInitialTheme = () => {
  applyThemeMode(APP_THEME_MODE);
  if (APP_THEME_MODE === "auto") {
    autoThemeInterval = window.setInterval(() => applyThemeMode("auto"), 60 * 1000);
  }
};
applyInitialTheme();

const normalizedConfig = computed(() =>
  sensorsConfig
    .filter(
      (item) =>
        Number.isInteger(item.num) &&
        item.num >= 0 &&
        item.num < MAX_SLOTS &&
        item.id &&
        item.name
    )
    .sort((a, b) => a.num - b.num)
);

const orderedCards = computed(() => {
  const dataMap = new Map(sensors.value.map((device) => [device.id, device]));
  const slots = Array.from({ length: MAX_SLOTS }, (_, index) => ({
    num: index,
    placeholder: true,
    name: `Slot ${index + 1}`,
  }));

  for (const item of normalizedConfig.value) {
    const target = slots[item.num];
    slots[item.num] = {
      num: item.num,
      name: item.name,
      data: dataMap.get(item.id),
      placeholder: !dataMap.has(item.id),
    };
  }

  return slots;
});

async function loadSensors() {
  if (DEBUG_MODE) {
    sensors.value = buildDebugSensors(sensorsConfig);
    return;
  }

  try {
    loading.value = true;
    error.value = null;
    const payload = await fetchSensors();
    sensors.value = payload;
  } catch (err) {
    console.error(err);
    error.value = err.message || "Impossible de récupérer les capteurs";
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadSensors();
  intervalId = window.setInterval(loadSensors, POLL_INTERVAL);
});

onUnmounted(() => {
  window.clearInterval(intervalId);
  if (autoThemeInterval) {
    window.clearInterval(autoThemeInterval);
  }
});
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: clamp(16px, 4vw, 40px);
}

.dashboard__debug-banner {
  background: #ffecb3;
  color: #5d4037;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  padding: 10px 16px;
  margin-bottom: 16px;
  font-weight: 600;
  text-align: center;
  letter-spacing: 0.3px;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

@media (min-width: 1024px) {
  .dashboard__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
