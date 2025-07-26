FROM node:22.12.0-alpine

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package*.json pnpm-lock.yaml ./
COPY pnpm-workspace.yaml ./

# Copy packages
COPY packages/ ./packages/
COPY turbo.json ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm build

# Expose port
EXPOSE 10000

# Set environment
ENV NODE_ENV=production
ENV PORT=10000

# Start the autonomous Eliza
CMD ["pnpm", "start"]
