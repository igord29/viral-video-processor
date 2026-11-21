# Dockerfile for Railway deployment

# Node.js 22+ is required by yt-dlp to solve YouTube's JS challenges. Debian's own nodejs
# package is version 20, which yt-dlp rejects as too old, so take the binary from the official image.
FROM node:22-slim AS node-binary

FROM python:3.11-slim

COPY --from=node-binary /usr/local/bin/node /usr/local/bin/node

# Install system dependencies for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads videos clips

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "web_app.py"]

