FROM python:3.7-slim-buster

WORKDIR /cowin-app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
WORKDIR /
ENTRYPOINT ["bokeh", "serve" , "--port", "5100","cowin-app/"]