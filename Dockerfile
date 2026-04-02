FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir requests
COPY messages.py /app/messages.py
COPY bot.py /app/bot.py
CMD ["python", "-u", "/app/bot.py"]