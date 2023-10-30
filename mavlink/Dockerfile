FROM python:3.8.10

ENV PYTHONIOENCODING utf-8
ENV TZ="Asia/Tokyo"
ENV LANG=C.UTF-8
ENV LANGUAGE=en_US:en_US

WORKDIR /tmp

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

# VOLUME [ "/app" ]
WORKDIR /home/app
COPY ./app/measure_square.py /home/app/measure_square.py

CMD ["bash"]

# docker build . -t test_mavlink
# docker run --rm -it test_mavlink bash
# docker run --rm -v ./app:/home/app -it test_mavlink bash
