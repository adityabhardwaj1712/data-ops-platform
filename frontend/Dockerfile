FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY tsconfig.json ./
COPY next.config.js ./
COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
