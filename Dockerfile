FROM python:3.7.10-stretch

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . /app

RUN python download_dependencies.py

CMD python app.py