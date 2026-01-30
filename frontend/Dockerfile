FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install --no-audit --no-fund

# 👇 THIS IS CRITICAL
COPY tsconfig.json ./
COPY next.config.js ./

COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]

