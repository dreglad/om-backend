#!/bin/bash

celery -A live2vod worker -l info --concurrency 1 -E
# bash
