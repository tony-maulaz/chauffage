const THEME_MODES = ["light", "dark", "auto"];

const resolveThemeMode = () => {
  const mode = (import.meta.env.VITE_THEME_MODE || "light").toLowerCase();
  return THEME_MODES.includes(mode) ? mode : "light";
};

const APP_THEME_MODE = resolveThemeMode();

export { APP_THEME_MODE };
