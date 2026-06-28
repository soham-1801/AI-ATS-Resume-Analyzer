FROM python:3.11-slim

WORKDIR /workspace

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set directory scope
WORKDIR /workspace/backend

# Copy backend application source
COPY backend/app ./app
COPY backend/alembic ./alembic
COPY backend/alembic.ini ./

# DO NOT COPY .env — pass secrets at runtime via -e or --env-file
# This prevents secrets from being baked into the image

# Run database migrations on startup
RUN alembic upgrade head || true

EXPOSE 8000

# Run production server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
