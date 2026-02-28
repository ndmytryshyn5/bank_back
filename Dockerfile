FROM python:3

RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]