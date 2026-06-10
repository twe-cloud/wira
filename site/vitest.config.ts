import { defineConfig } from "vitest/config";

// Dedicated vitest config (does NOT pull in the React/Tailwind Vite plugins) —
// the Worker is plain TS and tests run under node.
export default defineConfig({
  test: {
    environment: "node",
    include: ["cloudflare/**/*.test.ts", "src/**/*.test.ts"],
  },
});
