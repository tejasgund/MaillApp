FROM python:3.12-slim

RUN useradd -m TEJAS

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mail.py .

USER TEJAS

CMD ["python", "mail.py"]
