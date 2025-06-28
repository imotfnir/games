FROM python:3.13.0-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY .env ./
COPY discord-bot.py ./

CMD ["python", "-u", "discord-bot.py"]
