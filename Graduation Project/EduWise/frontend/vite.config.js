import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), 'EDUFLOW_');
  const proxy = {
    '^/api(?:/|$)': { target: env.EDUFLOW_API_TARGET || 'http://127.0.0.1:8787', changeOrigin: false },
  };
  return {
    plugins: [react(), tailwindcss()],
    server: {
      port: 5173, strictPort: true, proxy,
      fs: { deny: ['.env', '.env.*', '*.{crt,pem}', '**/.git/**', '**/server/**', '**/accounts.json', '**/workspace.json', '**/workspace-*.tmp'] },
    },
    preview: { port: 4173, strictPort: true, proxy },
  };
});
