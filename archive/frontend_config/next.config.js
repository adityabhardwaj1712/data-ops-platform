/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Static export for nginx
  images: {
    unoptimized: true,  // Required for static export
  },
  // Disable build-time checks for faster builds
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
