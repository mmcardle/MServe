from django import forms
from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import ManagementProperty
from django.forms import ModelForm
from django.forms import MultipleChoiceField

class HostingContainerForm(ModelForm):
    class Meta:
        exclude=['id','status']
        model = HostingContainer

class ManagementPropertyForm(ModelForm):
    class Meta:
        exclude=['base']
        model = ManagementProperty

class DataServiceURLForm(ModelForm):
    class Meta:
        exclude=['id','status','container']
        model = DataService

class DataServiceForm(ModelForm):
    cid = forms.CharField(max_length=50,widget=forms.HiddenInput)
    
    class Meta:
        exclude=['id','status','container']
        model = DataService

class DataStagerURLForm(ModelForm):
    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster']
        model = DataStager

class DataStagerForm(ModelForm):
    sid = forms.CharField(max_length=50,widget=forms.HiddenInput)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster']
        model = DataStager

class UpdateDataStagerForm(ModelForm):
    sid = forms.CharField(max_length=50,widget=forms.HiddenInput)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster']
        model = DataStager

class UpdateDataStagerFormURL(ModelForm):

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster']
        model = DataStager

class DataStagerAuthForm(ModelForm):
    dsid = forms.CharField(max_length=50,widget=forms.HiddenInput)
    roles = forms.CharField(max_length=200,label='Roles (comma separated)')
    class Meta:
        exclude=['id','methods_encoded','stager']
        model = DataStagerAuth

class SubAuthForm(ModelForm):
    roles_csv = forms.CharField(max_length=200,label='Roles (comma separated)')
    id_parent = forms.CharField(max_length=200,widget=forms.HiddenInput)
    class Meta:
        exclude=['id','methods_encoded']
        model = SubAuth