FROM python:3.11-slim

# Install Docker CLI within the container
RUN apt-get update && apt-get install -y --no-install-recommends \
    docker.io \
    # or curl and download static binary if you prefer a specific version
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["bash", "-c", "python manage.py migrate && python manage.py createsuperuser --no-input && python manage.py runserver 0.0.0.0:8001"]