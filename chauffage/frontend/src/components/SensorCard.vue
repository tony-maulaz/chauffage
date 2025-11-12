<template>
  <v-card
    :class="[
      'sensor-card',
      {
        'sensor-card--stale': isStale,
        'sensor-card--placeholder': isPlaceholder,
      },
    ]"
    elevation="8"
  >
    <template v-if="!isPlaceholder">
      <div class="sensor-card__content">
        <div class="sensor-card__main">
          <p class="sensor-card__reading">
            {{ formattedReading }}
          </p>
          <p class="sensor-card__name">
            {{ displayName }}
          </p>
          <div class="sensor-card__footer">
            <span class="sensor-card__timestamp-wrapper">
              <span
                class="sensor-card__timestamp"
                :class="{ 'sensor-card__timestamp--alert': isVeryStale }"
              >
                {{ updateLabel }}
              </span>
              <span v-if="isVeryStale" class="sensor-card__timestamp-pill">4h+</span>
            </span>
            <span
              v-if="hasSetpoint"
              class="sensor-card__setpoint"
            >
              {{ setpointLabel }}
            </span>
          </div>
        </div>
        <div class="sensor-card__side">
          <component :is="batteryComponent" class="sensor-card__battery" />
          <div v-if="regulationMode" class="sensor-card__regulation" :title="regulationTitle">
            <span :class="['sensor-card__regulation-icon', `sensor-card__regulation-icon--${regulationMode}`]">
              {{ regulationSymbol }}
            </span>
          </div>
          <span :class="['sensor-card__reachable', { 'sensor-card__reachable--down': !reachable }]">
            {{ reachable ? "OK" : "OFF" }}
          </span>
        </div>
      </div>
    </template>
    <div v-else class="sensor-card__placeholder-text">
      —
    </div>
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import BatteryLowIcon from "@/components/icons/BatteryLowIcon.vue";
import BatteryOkIcon from "@/components/icons/BatteryOkIcon.vue";

const props = defineProps({
  name: { type: String, default: "" },
  temperature: { type: Number, default: null },
  humidity: { type: Number, default: null },
  lastUpdate: { type: String, default: null },
  batteryLow: { type: Boolean, default: null },
  reachable: { type: Boolean, default: true },
  placeholder: { type: Boolean, default: false },
  setpointTemperature: { type: Number, default: null },
  regulationStatus: { type: String, default: null },
});

const displayName = computed(() => props.name || "—");
const isPlaceholder = computed(() => props.placeholder);

const formattedReading = computed(() => {
  if (isPlaceholder.value) return "— / —";
  const temp =
    props.temperature !== null && props.temperature !== undefined
      ? `${props.temperature.toFixed(1)}°C`
      : "—°C";
  const hum =
    props.humidity !== null && props.humidity !== undefined
      ? `${Math.round(props.humidity)}%`
      : "—%";
  return `${temp} / ${hum}`;
});

const batteryComponent = computed(() =>
  props.batteryLow ? BatteryLowIcon : BatteryOkIcon
);

const hasSetpoint = computed(
  () =>
    props.setpointTemperature !== null && props.setpointTemperature !== undefined
);

const setpointLabel = computed(() =>
  hasSetpoint.value ? `SP ${props.setpointTemperature.toFixed(1)}°C` : ""
);

const regulationMode = computed(() =>
  props.regulationStatus ? props.regulationStatus.toLowerCase() : null
);

const regulationSymbol = computed(() =>
  regulationMode.value === "cold" ? "❄" : "🔥"
);

const regulationTitle = computed(() => {
  if (!regulationMode.value) return "";
  return regulationMode.value === "cold" ? "Demande de froid" : "Demande de chaud";
});

const updateLabel = computed(() => {
  if (!props.lastUpdate) return "—";
  const date = new Date(props.lastUpdate);
  if (Number.isNaN(date.getTime())) return "—";
  const day = date.toLocaleDateString(undefined, { day: "2-digit", month: "2-digit" });
  const time = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return `${day} ${time}`;
});

const isStale = computed(() => {
  if (!props.lastUpdate) return true;
  const last = new Date(props.lastUpdate).getTime();
  return Date.now() - last > 5 * 60 * 1000; // >5 minutes
});

const isVeryStale = computed(() => {
  if (!props.lastUpdate) return true;
  const last = new Date(props.lastUpdate).getTime();
  return Date.now() - last > 4 * 60 * 60 * 1000; // >4h
});
</script>

<style scoped>
.sensor-card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: 20px;
  padding: 12px 18px;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease, border 0.2s ease, background 0.2s ease;
  border: 1px solid rgba(20, 20, 30, 0.06);
  color: #0f111a;
}

.v-theme--dashboardDark .sensor-card {
  background: rgba(19, 20, 27, 0.95);
  border-color: rgba(255, 255, 255, 0.08);
  color: #f4f6ff;
}

.sensor-card--placeholder {
  opacity: 0.4;
  border-style: dashed;
}

.sensor-card--stale:not(.sensor-card--placeholder) {
  border-color: rgba(255, 193, 7, 0.8);
}

.sensor-card__content {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.sensor-card__main {
  flex: 1;
}

.sensor-card__reading {
  font-size: clamp(1.8rem, 2.8vw, 3rem);
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.sensor-card__name {
  font-size: 1.05rem;
  margin: 4px 0 0;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  opacity: 0.75;
}

.sensor-card__footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  opacity: 0.8;
  align-items: center;
}

.sensor-card__timestamp-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sensor-card__timestamp {
  font-variant-numeric: tabular-nums;
  font-size: 0.85rem;
}

.sensor-card__timestamp--alert {
  color: #ef5350;
  font-weight: 600;
}

.sensor-card__timestamp-pill {
  font-size: 0.75rem;
  background-color: #ffebee;
  color: #c62828;
  padding: 0px 6px;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.v-theme--dashboardDark .sensor-card__timestamp--alert {
  color: #ff8a80;
}

.v-theme--dashboardDark .sensor-card__timestamp-pill {
  background-color: rgba(229, 115, 115, 0.2);
  color: #ffab91;
}

.sensor-card__setpoint {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e88e5;
}

.v-theme--dashboardDark .sensor-card__setpoint {
  color: #90caf9;
}

.sensor-card__side {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  min-width: 50px;
}

.sensor-card__battery {
  transition: transform 0.3s ease;
}

.sensor-card--stale .sensor-card__battery {
  animation: pulse 2s infinite;
}

.sensor-card__regulation {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 32px;
}

.sensor-card__regulation-icon {
  font-size: 1.4rem;
}

.sensor-card__regulation-icon--cold {
  color: #29b6f6;
}

.sensor-card__regulation-icon--hot {
  color: #ff7043;
}

.v-theme--dashboardDark .sensor-card__regulation-icon--cold {
  color: #4fc3f7;
}

.v-theme--dashboardDark .sensor-card__regulation-icon--hot {
  color: #ff8a65;
}

.sensor-card__reachable {
  font-weight: 600;
}

.sensor-card__reachable--down {
  color: #ef5350;
}

.sensor-card__placeholder-text {
  text-align: center;
  font-size: 2rem;
  opacity: 0.4;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}
</style>
