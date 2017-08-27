FROM debian:stretch
EXPOSE 5000
COPY . .
RUN apt-get update
RUN apt-get install -y wget python3.5
RUN wget https://bootstrap.pypa.io/get-pip.py

RUN python3.5 get-pip.py

RUN pip3 install -r requirements.txt
ENV FLASK_APP="run.py"
ENV APP_SETTINGS="development"
ENV MONGODB_URI="mongodb://admin:password@localhost"
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
CMD ["flask", "run", "--host=0.0.0.0"]
