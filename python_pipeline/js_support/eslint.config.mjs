import sonarjs from "eslint-plugin-sonarjs";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    ignores: [], 

    plugins: {
      sonarjs,
    },

    rules: {
      "sonarjs/cognitive-complexity": ["warn", 15],
    },
  },
]);