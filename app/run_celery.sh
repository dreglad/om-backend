#!/bin/bash

bash -c "python3 manage.py migrate && celery -A live2vod worker -Q celery -l info --concurrency 6 -E"
