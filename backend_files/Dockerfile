FROM python:3.11-slim

WORKDIR /app

# Install fundamental system development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip setuptools wheel

# Install matching structural packages that successfully load your model file
RUN pip install --no-cache-dir \
    flask==3.0.3 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    scikit-learn==1.5.1 \
    joblib==1.4.2 \
    xgboost==2.1.0

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
