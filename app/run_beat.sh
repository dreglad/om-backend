#!/bin/bash
sleep 5
bash -c "celery -A live2vod beat -l info"
