FROM python:3.11.9-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

WORKDIR /app

RUN apt-get update && apt-get install -y\
gcc\
&& rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip && 
pip install --no-cache-dir -r requirements.txt



COPY . .


EXPOSE 10000


CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "bot:app"]