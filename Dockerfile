FROM python:3.12

WORKDIR /io-service

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5050

COPY . .

CMD ["python", "io-service.py"]
