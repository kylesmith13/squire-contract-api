FROM python:latest

WORKDIR /app
COPY . .

CMD [ "python3", "api.py"]