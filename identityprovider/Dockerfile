FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["bash", "-c", "python manage.py migrate && python manage.py createsuperuser --no-input && python manage.py runserver 0.0.0.0:8001"]