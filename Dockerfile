FROM tiangolo/uwsgi-nginx-flask:flask
COPY ./app
WORKDIR /app
EXPOSE 8080
RUN pip install --upgrade pip
RUN pip install requests
RUN pip install sklearn
RUN pip install numpy
RUN pip install scipy
RUN pip install pandas
CMD ["make", "run"]