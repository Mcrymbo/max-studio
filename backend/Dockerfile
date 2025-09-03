FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

# Copy application code
COPY . .

# Create media directories
RUN mkdir -p media/jellyfin_library media/videos/originals media/videos/thumbnails media/videos/hls

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
