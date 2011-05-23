########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-03-25
#	Created for Project :		PrestoPrime
#
########################################################################
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
