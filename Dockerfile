FROM ghcr.io/osgeo/gdal:ubuntu-full-3.9.1
#FROM python:3.10

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    libpq-dev \
    build-essential \
    gcc \
	&& rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt --break-system-packages

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
