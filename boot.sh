#!/bin/bash
# This is used to boot a Docker container
flask deploy  # run custom flask cli command to create database
exec gunicorn -b :5000 --access-logfile - --error-logfile - annotations_interface:app
