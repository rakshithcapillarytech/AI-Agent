import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// The API runs separately (FastAPI on :8000); /api is proxied so the browser sees one origin.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
