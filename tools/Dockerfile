# Use Node.js LTS (Alpine for smaller size)
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json* ./

# Install dependencies (ci for clean install if lockfile exists, else install)
RUN npm install

# Copy application source
COPY . .

# Build the application
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NODE_ENV=production

# Start the application
CMD ["node", ".output/server/index.mjs"]
