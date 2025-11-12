const DEBUG_MODE =
  String(import.meta.env.VITE_DEBUG_MODE ?? "false").toLowerCase() === "true";

const minutesAgo = (mins) =>
  new Date(Date.now() - mins * 60 * 1000).toISOString();

const buildDebugSensors = (layout = []) =>
  layout.map((sensor, index) => ({
    id: sensor.id,
    label: sensor.name,
    temperature: 17 + (index % 6) * 1.7,
    humidity: 35 + ((index * 7) % 30),
    battery_low: index % 3 === 1,
    reachable: index % 4 !== 3,
    last_update: minutesAgo(
      index === 0 ? 5 * 60 : (index % 10) * 3 // slot 0 simulé > 4h pour alerte
    ),
    setpoint_temperature: 18 + ((index * 1.3) % 6),
    regulation_status: index % 2 === 0 ? "hot" : "cold",
  }));

export { DEBUG_MODE, buildDebugSensors };
