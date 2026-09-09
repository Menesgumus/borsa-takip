import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react({
    jsxRuntime: 'automatic'
  })],
  test: {
    environment: 'jsdom',
    exclude: ['node_modules', 'tests/e2e/**'],
    alias: {
      '@': path.resolve(__dirname, './')
    }
  }
})
