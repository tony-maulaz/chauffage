<template>
  <v-app class="dashboard-app">
    <v-main>
      <div class="dashboard">
        <header class="dashboard__header">
          <div>
            <h1>Températures</h1>
            <p>
              Mise à jour :
              <span>{{ lastRefreshLabel }}</span>
            </p>
          </div>
          <div class="dashboard__actions">
            <v-btn
              icon="mdi-fullscreen"
              variant="text"
              @click="toggleFullscreen"
            ></v-btn>
            <v-btn
              icon="mdi-refresh"
              variant="text"
              :loading="loading"
              @click="loadSensors"
            ></v-btn>
          </div>
        </header>

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
          density="comfortable"
        >
          {{ error }}
        </v-alert>

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
import { fetchSensors } from "@/services/api";
import SensorCard from "@/components/SensorCard.vue";

const POLL_INTERVAL = Number(import.meta.env.VITE_POLL_INTERVAL || 60000);
const MAX_SLOTS = 12;

const sensors = ref([]);
const loading = ref(false);
const error = ref(null);
const lastRefresh = ref(null);
let intervalId;

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

const lastRefreshLabel = computed(() => {
  if (!lastRefresh.value) return "—";
  return lastRefresh.value.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
});

async function loadSensors() {
  try {
    loading.value = true;
    error.value = null;
    const payload = await fetchSensors();
    sensors.value = payload;
    lastRefresh.value = new Date();
  } catch (err) {
    console.error(err);
    error.value = err.message || "Impossible de récupérer les capteurs";
  } finally {
    loading.value = false;
  }
}

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen?.();
  } else {
    document.exitFullscreen?.();
  }
}

onMounted(() => {
  loadSensors();
  intervalId = window.setInterval(loadSensors, POLL_INTERVAL);
});

onUnmounted(() => {
  window.clearInterval(intervalId);
});
</script>

<style scoped>
.dashboard-app {
  background: radial-gradient(circle at top, #1f1f2f, #0c0c12);
}

.dashboard {
  min-height: 100vh;
  padding: 24px clamp(16px, 5vw, 48px) 40px;
  color: #fafafa;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.dashboard__header h1 {
  margin: 0;
  font-size: 1.8rem;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.dashboard__header p {
  margin: 4px 0 0;
  opacity: 0.7;
}

.dashboard__actions {
  display: flex;
  gap: 8px;
}

.dashboard__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

@media (min-width: 1024px) {
  .dashboard__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
