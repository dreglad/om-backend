#!/bin/bash

celery -A live2vod worker -l info --concurrency 3 -E
# bash
