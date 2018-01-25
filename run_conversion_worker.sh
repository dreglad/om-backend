#!/bin/bash

celery -A live2vod worker -Q conversions -l debug --concurrency 1 -E
