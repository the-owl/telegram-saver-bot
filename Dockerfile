FROM python:3.8

RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN pip install -r requirements.txt
COPY ./*.py /app

CMD ["python", "main.py"]
