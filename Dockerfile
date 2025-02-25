FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies as non-root user
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install transformers

# Copy the rest of the application
COPY . .

# Create directory for mounted secrets
RUN mkdir -p /etc/secrets && \
    chmod -R 755 /etc/secrets

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with debug logging
CMD gunicorn --bind 0.0.0.0:$PORT --log-level debug app:app
