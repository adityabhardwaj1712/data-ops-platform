# ================================
# FRONTEND – LOW DISK SAFE BUILD
# ================================

# -------- Stage 1: Build --------
FROM node:20-alpine AS builder

WORKDIR /app

# Reduce npm cache size
ENV npm_config_cache=/tmp/.npm

# Copy only required files first (better cache)
COPY package.json package-lock.json* ./

# Install deps (prod + build deps)
RUN npm install --legacy-peer-deps --no-audit --no-fund

# Copy source
COPY . .

# Build Next.js (static export)
RUN npm run build

# -------- Stage 2: Runtime --------
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy ONLY the build output
COPY --from=builder /app/out /usr/share/nginx/html

# Expose frontend port
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

