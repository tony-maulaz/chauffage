import { computed } from "vue";
import { useTheme } from "vuetify";
import { themeNames } from "@/plugins/vuetify";

const allowedThemes = Object.values(themeNames);
const DAY_START = 7;
const DAY_END = 19;

const isDaytime = () => {
  const hour = new Date().getHours();
  return hour >= DAY_START && hour < DAY_END;
};

export function useThemeController() {
  const theme = useTheme();

  const setTheme = (name) => {
    if (allowedThemes.includes(name)) {
      theme.global.name.value = name;
    }
  };

  const setLightTheme = () => setTheme(themeNames.light);
  const setDarkTheme = () => setTheme(themeNames.dark);

  const applyThemeMode = (mode = "light") => {
    const normalized = mode.toLowerCase();
    if (normalized === "dark") {
      setDarkTheme();
    } else if (normalized === "auto") {
      setTheme(isDaytime() ? themeNames.light : themeNames.dark);
    } else {
      setLightTheme();
    }
  };

  return {
    themeName: computed(() => theme.global.name.value),
    setTheme,
    setLightTheme,
    setDarkTheme,
    applyThemeMode,
  };
}
