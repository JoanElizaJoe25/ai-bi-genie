# Stage 1: Build React Frontend
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend + Serve Frontend
FROM python:3.12-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/frontend/build ./static

# Set environment variables
ENV PORT=8080
ENV GCP_PROJECT=sada-seed-2025-sandbox
ENV BQ_DATASET=intern_a_ecommerce
ENV LOCATION=us-central1
ENV GEMINI_MODEL=gemini-2.5-flash
ENV MAX_BYTES_BILLED=104857600
ENV MAX_REQUESTS_PER_MINUTE=20
ENV MAX_CONVERSATION_TURNS=6

# Expose port
EXPOSE 8080

# Start the server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]