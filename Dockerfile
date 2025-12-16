# Stage 1: Build the React frontend
FROM node:16 as builder

WORKDIR /app

# Install babel to transpile JSX
RUN npm install @babel/cli @babel/preset-react

# Copy the src
COPY frontend/src ./frontend/src

# Transpile JSX and create a single app.js
RUN ./node_modules/.bin/babel frontend/src --out-file frontend/app.js --presets=@babel/preset-react

# Stage 2: Create the final production image
FROM python:3.9-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt ./backend/requirements.txt

# Install Nginx, Python dependencies, and Gunicorn
RUN apt-get update && apt-get install -y nginx && \
    pip install --no-cache-dir gunicorn && \
    pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY backend/ ./backend
COPY frontend/ ./frontend

# Copy the built frontend app from the builder stage
COPY --from=builder /app/frontend/app.js ./frontend/app.js

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

# Set the entrypoint to the start script
CMD ["sh", "-c", "gunicorn --bind 127.0.0.1:5000 --workers 4 backend.app:app & nginx -g 'daemon off;'"]
