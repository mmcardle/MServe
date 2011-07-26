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
from django import forms
from dataservice.models import *
from django.forms import ModelForm
from static import *

ID_FIELD_LENGTH  = 200

class ServiceRequestForm(ModelForm):
    class Meta:
        exclude=['profile','state']
        model = ServiceRequest

class DataServiceTaskForm(ModelForm):
    class Meta:
        #exclude=['id','workflow','task_name','condition','allowremote','remotecondition']
        model = DataServiceTask

PROFILE_CHOICES = [  ]
for k in default_profiles:
    PROFILE_CHOICES.append( (k,k)  )

class HostingContainerForm(ModelForm):
    default_profile = forms.CharField(widget=forms.Select(choices=PROFILE_CHOICES),required=False, label="Services will be created with this profile")
    default_path    = forms.CharField(label='Path after %s (Dont include leading slash)' % (settings.STORAGE_ROOT), required=False)

    class Meta:
        exclude=['id','status','reportnum','initial_usage_recorded','usages','properties']
        model = HostingContainer

class ManagementPropertyForm(ModelForm):
    class Meta:
        exclude=['base']
        model = ManagementProperty

class DataServiceURLForm(ModelForm):
    class Meta:
        exclude=['id','status','container','reportnum','initial_usage_recorded','usages']
        model = DataService

class DataServiceForm(ModelForm):
    #cid = forms.CharField(max_length=50,widget=forms.HiddenInput)
    
    class Meta:
        exclude=['id', 'status', 'reportnum', 'initial_usage_recorded', 'usages']#,'starttime','endtime']
        model = DataService

class MFileURLForm(ModelForm):
    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum','initial_usage_recorded','usages','folder']
        model = MFile

class MFileForm(ModelForm):
    sid = forms.CharField(max_length=ID_FIELD_LENGTH,widget=forms.HiddenInput,required=False)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum','initial_usage_recorded','usages','proxy','folder']
        model = MFile

class UpdateMFileForm(ModelForm):
    sid = forms.CharField(max_length=ID_FIELD_LENGTH,widget=forms.HiddenInput)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum','initial_usage_recorded','usages','proxy','folder']
        model = MFile

class AuthForm(ModelForm):
    dsid = forms.CharField(max_length=ID_FIELD_LENGTH,widget=forms.HiddenInput)
    roles = forms.CharField(max_length=200,label='Roles (comma separated)')

    class Meta:
        exclude=['id','methods_encoded','base']
        model = Auth