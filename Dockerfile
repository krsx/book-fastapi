FROM python:3.10-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV HOST 0.0.0.0

CMD ["fastapi","run","src","--port","8000","--host","0.0.0.0"]