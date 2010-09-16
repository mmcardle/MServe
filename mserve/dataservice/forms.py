from django import forms
from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from django.forms import ModelForm

class HostingContainerForm(ModelForm):
    class Meta:
        exclude=['id','status']
        model = HostingContainer

class DataServiceForm(ModelForm):
    class Meta:
        exclude=['id','status','container']
        model = DataService

class DataStagerForm(ModelForm):
    class Meta:
        exclude=['name','id','status','service']
        model = DataStager

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class DataStagerAuthForm(ModelForm):
    methods_csv = forms.CharField(max_length=200)
    class Meta:
        exclude=['id','methods_encoded','stager']
        model = DataStagerAuth

class SubAuthForm(ModelForm):
    methods_csv = forms.CharField(max_length=200)
    class Meta:
        exclude=['id','methods_encoded','stager']
        model = DataStagerAuth