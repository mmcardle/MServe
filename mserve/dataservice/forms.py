from django import forms
from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from django.forms import ModelForm

class HostingContainerForm(ModelForm):
    class Meta:
        exclude=['id','status']
        model = HostingContainer

class DataServiceForm(ModelForm):
    class Meta:
        exclude=['id','status']
        model = DataService

class DataStagerForm(ModelForm):
    class Meta:
        exclude=['name','id','status']
        model = DataStager

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()

class AuthForm(forms.Form):
    name = forms.CharField(max_length=100)
    roles = forms.CharField(max_length=100)
