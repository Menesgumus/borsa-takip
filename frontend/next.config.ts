import type { NextConfig } from "next";
import withPWAInit from "@ducanh2912/next-pwa";

const withPWA = withPWAInit({
  dest: "public",
  disable: process.env.NODE_ENV === "development" || process.env.DISABLE_PWA === "true",
  register: true,
  cacheOnFrontEndNav: false, // Prevents stale page caches during heavy dev/QA
  aggressiveFrontEndNavCaching: false,
  reloadOnOnline: true,
  workboxOptions: {
    // Explicitly exclude API routes from being cached by the service worker
    exclude: [/\/api\/.*/],
  }
});

const nextConfig: NextConfig = {
  output: process.env.NEXT_STANDALONE ? 'standalone' : undefined,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: (process.env.INTERNAL_API_URL || 'http://127.0.0.1:8001') + '/api/v1/:path*',
      },
    ];
  },
};

export default withPWA(nextConfig);
