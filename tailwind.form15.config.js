/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./form15_tra/templates/**/*.html",
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Cairo", "sans-serif"],
      },
      colors: {
        primary: "#1e40af",
        secondary: "#d97706",
      },
    },
  },
  plugins: [],
};

