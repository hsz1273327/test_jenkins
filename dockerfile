FROM python:latest
ADD ./test_drone /code/test_drone
ADD ./requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt