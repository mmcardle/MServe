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
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg, Max, Min, Count

ID_FIELD_LENGTH  = 200

class ServiceRequestForm(ModelForm):
    class Meta:
        exclude=['profile','state']
        model = ServiceRequest

class DataServiceTaskSetForm(ModelForm):

    def save(self, commit=True):
        instance = super(DataServiceTaskSetForm, self).save(commit=False)
        logging.info(self.cleaned_data)
        if instance.order == -1 and instance.id == None:
            max_order = instance.workflow.tasksets.aggregate(max_order=Max('order'))["max_order"] or -1 and 0
            instance.order = max_order +1

        '''if instance.order != -1 and instance.id != None:
            logging.info("XXX 1 %s" , instance)
            try:
                previnst = DataServiceTaskSet.objects.get(id=instance.id)
                logging.info("XXX 2 %s" , instance)
                previnstorder = previnst.order
                logging.info("XXX 3 %s" , previnstorder)
                try:
                    logging.info("XXX 3.2 %s" , previnstorder)
                    duplicateinstances = instance.workflow.tasksets.filter(order=previnstorder)
                    logging.info("XXX 4 %s" , duplicateinstances )
                    for duplicateinstance in duplicateinstances:
                        duplicateinstance.order = previnstorder
                        duplicateinstance.save()
                except ObjectDoesNotExist:
                    logging.info("XXX 5 %s" , instance)
                    raise e
            except Exception as e:
                raise e'''
        if commit:
            instance.save()
        logging.info("XXX %s" , instance)
        return instance

    class Meta:
        #exclude=['order',]
        model = DataServiceTaskSet

class DataServiceTaskForm(ModelForm):
    class Meta:
        model = DataServiceTask

PROFILE_CHOICES = [  ]
for k in default_profiles:
    PROFILE_CHOICES.append( (k,k)  )

class HostingContainerForm(ModelForm):
    default_profile = forms.CharField(widget=forms.Select(choices=PROFILE_CHOICES),required=False, label="Services will be created with this profile")
    default_path    = forms.CharField(label='Path after %s (Dont include leading slash)' % (settings.STORAGE_ROOT), required=False)

    class Meta:
        exclude=['id','reportnum','initial_usage_recorded','usages','properties']
        model = HostingContainer

class ManagementPropertyForm(ModelForm):
    class Meta:
        exclude=['base']
        model = ManagementProperty

class DataServiceURLForm(ModelForm):
    class Meta:
        exclude=['id','status','container','reportnum','initial_usage_recorded','usages','parent','priority']
        model = DataService

class SubServiceForm(ModelForm):
    serviceid = forms.CharField(max_length=50,widget=forms.HiddenInput,required=False)

    class Meta:
        exclude=['id', 'status', 'reportnum', 'initial_usage_recorded', 'usages','container','service','priority','parent']
        model = DataService

class DataServiceForm(ModelForm):
    name = forms.CharField(max_length=50,required=False)
    
    class Meta:
        exclude=['id', 'status', 'reportnum', 'initial_usage_recorded', 'usages','parent','priority','container']#,'starttime','endtime']
        model = DataService

class MFileURLForm(ModelForm):
    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum','initial_usage_recorded','usages','folder','duplicate_of']
        model = MFile

class MFileForm(ModelForm):
    sid = forms.CharField(max_length=ID_FIELD_LENGTH,widget=forms.HiddenInput,required=False)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum','initial_usage_recorded','usages','proxy','folder','duplicate_of']
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