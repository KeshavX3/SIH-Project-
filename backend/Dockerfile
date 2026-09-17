FROM python:3.11-slim

# Install system deps needed by psycopg2, geoalchemy2, shapely
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create directory for saved ML models
RUN mkdir -p app/ml/models

# Train ML model at build time so it's ready on startup
RUN python -c "from app.ml.training.train import train_and_save_model; train_and_save_model()" 2>/dev/null || echo "ML model will be trained on first startup"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
