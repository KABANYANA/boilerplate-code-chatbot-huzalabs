FROM python:3.10.5
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w 5", "-b 0.0.0.0:80", "app:app"]