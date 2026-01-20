FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application with environment variables
ARG VITE_API_BASE_URL
ARG VITE_WS_URL
ARG VITE_AI_API_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_URL=$VITE_WS_URL
ENV VITE_AI_API_URL=$VITE_AI_API_URL

# Build the application
RUN npm run build

# Expose port
EXPOSE 5173

# Start the application in development mode
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]