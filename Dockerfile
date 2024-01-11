FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt

#RUN apt update && apt install libmysqlclient-dev -y

#RUN pip3 install mysqlclient

# for transcoding the motion photos
RUN apt-get update && apt-get install -y ffmpeg --no-install-recommends && rm -rf /var/lib/apt/lists/*
#RUN apt install ffmpeg

RUN pip3 install -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--threads", "2", "--workers", "16", "--worker-class", "uvicorn.workers.UvicornWorker","--timeout", "90", "--bind", "0.0.0.0:8001"]
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]