from django.core.cache import cache

cache.set('dataservice.tasks.thumbimage', { "inputmime" : "application/octet-stream", "outputmime" : "image/png", "options" : ['width','height']} )