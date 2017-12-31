#!/bin/bash
celery -A live2vod worker -l debug --concurrency 1 -E
celery -A live2vod beat -l debug
# bash
