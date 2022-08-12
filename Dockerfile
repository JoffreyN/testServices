FROM harbor.cmbi.online/common/python:3.9-slim-bullseye
LABEL description='test service'

WORKDIR /application/testservices

COPY dependencies dependencies
RUN pip install --upgrade pip && pip3 install -r ./dependencies


COPY . .
RUN yes | python3 manage.py makemigrations


EXPOSE 8000
ENTRYPOINT  python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000 --insecure
