#!/bin/bash

celery -A live2vod worker -l debug --concurrency 1 -E
