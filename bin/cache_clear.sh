#!/bin/sh

echo "from django.core.cache import cache; cache.clear()" | ./manage.py shell 
