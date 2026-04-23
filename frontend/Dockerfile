# Stage 1: builder
FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/vite.config.js ./
COPY frontend/index.html ./
COPY frontend/src ./src


# Stage 2: runtime
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY frontend/package*.json ./
COPY frontend/vite.config.js ./
COPY frontend/index.html ./
COPY frontend/src ./src

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]