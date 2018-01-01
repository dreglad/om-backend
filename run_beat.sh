#!/bin/bash
sleep 5
celery -A live2vod beat -l debug
