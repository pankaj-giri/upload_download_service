FROM python:3.8-slim as base_image

WORKDIR /app

RUN mkdir p /app/data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM base_image AS app_build

COPY . ./

CMD exec gunicorn -b "0.0.0.0:8000" app:app