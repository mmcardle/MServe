from django import template
from django.template.defaultfilters import stringfilter
import os


register = template.Library()


@register.filter(name='basename')
@stringfilter
def basename(value):
    return os.path.basename(value)

@register.filter(name='startswith')
def startswith(value,arg):
    return value.startswith(arg)