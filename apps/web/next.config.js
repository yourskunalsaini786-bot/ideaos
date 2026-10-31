/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: process.env.API_URL || '/api/index.py',
      },
      {
        source: '/health',
        destination: process.env.API_URL ? `${process.env.API_URL}/health` : '/api/index.py',
      },
      {
        source: '/docs',
        destination: process.env.API_URL ? `${process.env.API_URL}/docs` : '/api/index.py',
      },
      {
        source: '/openapi.json',
        destination: process.env.API_URL ? `${process.env.API_URL}/openapi.json` : '/api/index.py',
      },
    ];
  },
};

module.exports = nextConfig;
