/** @type {import('next').NextConfig} */
const nextConfig = {
  trailingSlash: false,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE || 'http://backend:8000'}/api/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
