# specify base image
FROM python:3.10.0-slim

# create new user called annotations-interface
RUN useradd annotations-interface

# set working directory
WORKDIR /home/annotations-interface

# create a folder called "data" to store the user uploads
RUN mkdir data

# copy requirements to working directory and install them
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
# install gunicorn, to be used as a web server
RUN pip3 install gunicorn

# copy the rest of the files to working directory
COPY app app
COPY migrations migrations
COPY annotations_interface.py config.py boot.sh ./
# make boot.sh executable
RUN chmod +x boot.sh

# set environment variables for flask
ENV FLASK_APP annotations_interface.py

# change ownership of working directory to annotations-interface user
RUN chown -R annotations-interface:annotations-interface ./
# switch to annotations-interface user (makes it default user)
USER annotations-interface

# expose port 5000 for server (default port for flask)
EXPOSE 5000

# run boot.sh when container is run
ENTRYPOINT ["./boot.sh"]
