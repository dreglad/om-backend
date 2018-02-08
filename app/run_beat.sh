#!/bin/bash
sleep 5
bash -c "python3 manage.py migrate && celery -A live2vod beat -l info"
