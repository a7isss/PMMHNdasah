/** @type {import('next').NextConfig} */
const nextConfig = {
  // Railway deployment optimizations
  // experimental: {
  //   appDir: true, // Not needed in Next.js 15+
  // },

  // Environment variables
  env: {
    API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // Image domains for Railway (updated for Next.js 15)
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'railway.app',
        port: '',
        pathname: '/**',
      },
      {
        protocol: 'https',
        hostname: 'your-domain.com',
        port: '',
        pathname: '/**',
      },
    ],
  },

  // Build optimizations
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Compression and performance
  compress: true,

  // Output optimization
  output: 'standalone',

  // API rewrites for Railway backend proxying
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://fantastic-embrace.railway.internal/api/:path*',
      },
    ];
  },

  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
