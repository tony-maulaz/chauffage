import "vuetify/styles";
import { createVuetify } from "vuetify";
import { aliases, mdi } from "vuetify/iconsets/mdi";

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

export default createVuetify({
  theme: {
    defaultTheme: "dashboardDark",
    themes: {
      dashboardDark,
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
