import type { NextConfig } from "next";

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

export default nextConfig;
