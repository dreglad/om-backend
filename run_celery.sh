#!/bin/bash

celery -A live2vod worker -l info -E
