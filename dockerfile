FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=10000

WORKDIR /app

Install minimal system deps

RUN apt-get update && apt-get install -y 
gcc 
&& rm -rf /var/lib/apt/lists/*

Install Python deps

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

Copy app

COPY . .

Expose port

EXPOSE 10000

Start with gunicorn (bot.py file)

CMD ["gunicorn", "-b", "0.0.0.0:10000", "bot:app"]