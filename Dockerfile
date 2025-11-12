# syntax=docker/dockerfile:1.6

### Frontend build stage ######################################################
FROM node:20-slim AS frontend-builder

WORKDIR /app/frontend
COPY chauffage/frontend/package*.json ./
RUN npm ci

COPY chauffage/frontend/ .
RUN npm run build


### Backend runtime ###########################################################
FROM python:3.12-slim AS backend

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY chauffage/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chauffage ./chauffage
COPY --from=frontend-builder /app/frontend/dist ./chauffage/frontend/dist

EXPOSE 8000

CMD ["uvicorn", "chauffage.main:app", "--host", "0.0.0.0", "--port", "8000"]
