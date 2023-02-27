FROM python:3.10-alpine

WORKDIR /homework_11

COPY requirements.txt .

RUN pip install -U pip
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["pytest"]
