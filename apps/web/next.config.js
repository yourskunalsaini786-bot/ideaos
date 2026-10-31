/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // In local development, proxy to local FastAPI on port 8000
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/v1/:path*',
          destination: 'http://127.0.0.1:8000/api/v1/:path*',
        },
        {
          source: '/health',
          destination: 'http://127.0.0.1:8000/health',
        },
      ];
    }
    // If API_URL is configured in environment, proxy to it
    if (process.env.API_URL) {
      return [
        {
          source: '/api/v1/:path*',
          destination: `${process.env.API_URL}/api/v1/:path*`,
        },
        {
          source: '/health',
          destination: `${process.env.API_URL}/health`,
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;
