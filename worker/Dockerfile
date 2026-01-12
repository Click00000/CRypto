FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements and install
COPY ../backend/requirements.txt /tmp/backend-requirements.txt
RUN pip install --no-cache-dir -r /tmp/backend-requirements.txt

# Copy backend code
COPY ../backend /app/backend

# Install worker requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app/backend:$PYTHONPATH

CMD ["sh", "-c", "celery -A app.celery_app worker --loglevel=info & celery -A app.celery_app beat --loglevel=info"]
