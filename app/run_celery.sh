#!/bin/bash

celery -A live2vod worker -Q celery -l debug --concurrency 6 -E
