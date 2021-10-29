FROM python:3.9-alpine3.14

RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
ENV PYTHONPATH /app
RUN pip install -r requirements.txt
COPY saver_bot /app/saver_bot
COPY config.yaml /app

CMD ["python", "saver_bot/main.py"]
