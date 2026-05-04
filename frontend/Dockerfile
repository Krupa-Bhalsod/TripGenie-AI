# frontend/Dockerfile
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build

# Runner stage
FROM node:20-slim AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]
