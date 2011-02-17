from django import template
from django.template.defaultfilters import stringfilter
import os

register = template.Library()

@register.filter(name='basename')
@stringfilter
def basename(value):
    return os.path.basename(value)

@register.filter(name='startswith')
@stringfilter
def startswith(value,arg):
    return value.startswith(arg)

@register.filter(name='endswith')
@stringfilter
def endswith(value,arg):
    return value.endswith(arg)

@register.filter(name='trunc')
@stringfilter
def trunc(value,length):
    return (value[:length] + '..') if len(value) > length else value
