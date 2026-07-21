FROM python:3.14-alpine

# Install build dependencies for Pillow and pillow-heif
RUN apk add --no-cache \
    gcc \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    libheif-dev \
    build-base \
    pkgconf

# Install Python dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Create directories
RUN mkdir -p /images /data

# Copy application files
COPY app.py /app/app.py
COPY VERSION /app/VERSION
RUN chmod +x /app/app.py

# Set working directory
WORKDIR /app

# Default command
CMD ["python", "-u", "app.py"]