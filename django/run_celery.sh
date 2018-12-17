#!/bin/bash

bash -c "celery -A live2vod worker -Q celery -l info --concurrency 8 -E"
