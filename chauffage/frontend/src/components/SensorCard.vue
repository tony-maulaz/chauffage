<template>
  <v-card
    :class="[
      'sensor-card',
      { 'sensor-card--stale': isStale, 'sensor-card--placeholder': isPlaceholder },
    ]"
    elevation="4"
  >
    <div class="sensor-card__top">
      <p class="sensor-card__reading">
        {{ formattedReading }}
      </p>
      <v-icon
        v-if="!isPlaceholder"
        :icon="batteryIcon"
        :color="batteryColor"
        class="sensor-card__battery"
        size="32"
      />
    </div>

    <p class="sensor-card__name">
      {{ displayName }}
    </p>

    <div v-if="!isPlaceholder" class="sensor-card__meta">
      <span>{{ updateLabel }}</span>
      <span :class="{ 'sensor-card__reachable--down': !reachable }">
        {{ reachable ? "OK" : "OFF" }}
      </span>
    </div>

    <div v-else class="sensor-card__placeholder-text">
      —
    </div>
  </v-card>
</template>

<script setup>
import { computed } from "vue";
import { mdiBattery, mdiBatteryAlertVariantOutline } from "@mdi/js";

const props = defineProps({
  name: { type: String, default: "" },
  temperature: { type: Number, default: null },
  humidity: { type: Number, default: null },
  lastUpdate: { type: String, default: null },
  batteryLow: { type: Boolean, default: null },
  reachable: { type: Boolean, default: true },
  placeholder: { type: Boolean, default: false },
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

const batteryIcon = computed(() =>
  props.batteryLow ? mdiBatteryAlertVariantOutline : mdiBattery
);

const batteryColor = computed(() =>
  props.batteryLow ? "error" : "success"
);

const updateLabel = computed(() => {
  if (!props.lastUpdate) return "—";
  const date = new Date(props.lastUpdate);
  if (Number.isNaN(date.getTime())) return "—";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
});

const isStale = computed(() => {
  if (!props.lastUpdate) return true;
  const last = new Date(props.lastUpdate).getTime();
  return Date.now() - last > 5 * 60 * 1000; // >5 minutes
});
</script>

<style scoped>
.sensor-card {
  background: rgba(20, 20, 24, 0.9);
  border-radius: 18px;
  padding: 18px;
  min-height: 160px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease, border 0.2s ease, background 0.2s ease;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.sensor-card--placeholder {
  opacity: 0.4;
  border-style: dashed;
}

.sensor-card--stale:not(.sensor-card--placeholder) {
  border-color: rgba(255, 193, 7, 0.8);
}

.sensor-card__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.sensor-card__reading {
  font-size: clamp(1.6rem, 2.5vw, 2.8rem);
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.sensor-card__battery {
  transition: transform 0.3s ease;
}

.sensor-card--stale .sensor-card__battery {
  animation: pulse 2s infinite;
}

.sensor-card__name {
  font-size: 1rem;
  margin: 4px 0 0;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  opacity: 0.85;
}

.sensor-card__meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  opacity: 0.85;
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
