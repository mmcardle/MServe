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
from jobservice.models import *
from django.contrib import admin

class TaskOptionInline(admin.StackedInline):
    model = TaskOption
    extra = 0
    #max_num = 0
    #can_delete = False
    #readonly_fields = ("name",)

class TaskResultInline(admin.StackedInline):
    model = TaskResult
    extra = 0
    #max_num = 0
    #can_delete = False
    #readonly_fields = ("name",)

class TaskOutputInline(admin.StackedInline):
    model = TaskOutput
    extra = 0
    #max_num = 0
    #can_delete = False
    #readonly_fields = ("mimetype", "num")

class TaskInputInline(admin.StackedInline):
    model = TaskInput
    extra = 0
    #max_num = 0
    #can_delete = False
    #readonly_fields = ("mimetype", "num")
    
class TaskDescriptionAdmin(admin.ModelAdmin):
    inlines = [
        TaskInputInline, TaskOptionInline, TaskOutputInline, TaskResultInline
    ]

admin.site.register(TaskDescription, TaskDescriptionAdmin)
admin.site.register(Job)
admin.site.register(JobOutput)