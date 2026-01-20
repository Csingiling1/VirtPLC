import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 3000,
    proxy: {
      '/api': {
        // Proxy API requests to the backend service inside Docker network
        target: 'http://backend:8080',
        changeOrigin: true,
        secure: false,
      },
      '/auth': {
        // Proxy auth requests to the backend service inside Docker network
        target: 'http://backend:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [react(), mode === "development" && componentTagger()].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React and core libraries
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI libraries - split Radix UI components
          'radix-ui': [
            '@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select',
            '@radix-ui/react-toast', '@radix-ui/react-tooltip', '@radix-ui/react-popover',
            '@radix-ui/react-accordion', '@radix-ui/react-tabs', '@radix-ui/react-collapsible'
          ],
          // Charts and visualization
          'charts-vendor': ['recharts', 'chart.js', 'react-chartjs-2'],
          // HTTP client and utilities
          'http-vendor': ['axios', '@tanstack/react-query'],
          // Form handling
          'forms-vendor': ['react-hook-form', '@hookform/resolvers'],
          // Date utilities
          'date-vendor': ['date-fns'],
          // Drag and drop
          'dnd-vendor': ['@dnd-kit/core', '@dnd-kit/sortable', '@dnd-kit/utilities'],
          // Icons and UI utilities
          'ui-utils': ['lucide-react', 'cmdk', 'input-otp', 'html2canvas'],
          // Animation and theming
          'theme-vendor': ['next-themes', 'tailwindcss-animate', 'sonner'],
        },
      },
    },
    // Increase chunk size warning limit
    chunkSizeWarningLimit: 1000,
  },
}));
