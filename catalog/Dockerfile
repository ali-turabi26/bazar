FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN mkdir -p /data
CMD ["python", "app.py"]
