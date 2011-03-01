from django.core.cache import cache

cache.set('jobservice.tasks.render_blender', { "inputmime" : "application/octet-stream", "outputmime" : "image/png", "options" : ['frame']} )