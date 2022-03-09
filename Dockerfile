FROM python:latest

RUN pip install web3 flask

WORKDIR /app
COPY . .

CMD [ "python3", "api.py"]