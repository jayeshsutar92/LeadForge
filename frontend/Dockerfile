FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy all source files
COPY . .

# Build the Node.js server (Nitro preset)
ENV NITRO_PRESET=node-server
RUN npm run build

# Production image
FROM node:20-alpine AS runner

WORKDIR /app

# Copy output from builder
COPY --from=builder /app/.output ./.output

# Expose port 80 since docker-compose maps 3000:80
EXPOSE 80

ENV PORT=80
ENV HOST=0.0.0.0
ENV NODE_ENV=production

CMD ["node", ".output/server/index.mjs"]
