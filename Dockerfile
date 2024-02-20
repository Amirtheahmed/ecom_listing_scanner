FROM python:3.10-slim

WORKDIR /usr/src/app

COPY . .

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python3.10", "-m","src.main"]