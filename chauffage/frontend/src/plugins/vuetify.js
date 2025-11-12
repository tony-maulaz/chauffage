import "vuetify/styles";
import { createVuetify } from "vuetify";
import { aliases, mdi } from "vuetify/iconsets/mdi";

const dashboardLight = {
  dark: false,
  colors: {
    background: "#f6f7fb",
    surface: "#ffffff",
    primary: "#5c6ac4",
    secondary: "#4c6ef5",
    error: "#ef5350",
    warning: "#ffb300",
    success: "#43a047",
    info: "#1e88e5",
  },
};

const dashboardDark = {
  dark: true,
  colors: {
    background: "#050507",
    surface: "#151521",
    primary: "#7b61ff",
    secondary: "#26c6da",
    error: "#ff6b6b",
    warning: "#ffca28",
    success: "#4caf50",
    info: "#64b5f6",
  },
};

export const themeNames = {
  light: "dashboardLight",
  dark: "dashboardDark",
};

const vuetify = createVuetify({
  theme: {
    defaultTheme: themeNames.light,
    themes: {
      [themeNames.light]: dashboardLight,
      [themeNames.dark]: dashboardDark,
    },
  },
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
});

export default vuetify;
