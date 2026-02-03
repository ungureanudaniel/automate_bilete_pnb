# Dockerfile
FROM python:3.12.3-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Create non-root user
RUN adduser --disabled-password --gecos '' django
RUN chown -R django:django /app
USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "server_automate_main.wsgi:application"]
CMD ["sh", "-c", "export DJANGO_SETTINGS_MODULE=bucegi_admin.settings && python manage.py migrate && gunicorn --bind 0.0.0.0:8000 server_automate_main.wsgi:application"]