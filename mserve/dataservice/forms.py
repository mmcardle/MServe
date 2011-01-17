from django import forms
from dataservice.models import *
from django.forms import ModelForm
from django.forms import MultipleChoiceField

class HostingContainerForm(ModelForm):
    class Meta:
        exclude=['id','status','reportnum']
        model = HostingContainer

class ManagementPropertyForm(ModelForm):
    class Meta:
        exclude=['base']
        model = ManagementProperty

class DataServiceURLForm(ModelForm):
    class Meta:
        exclude=['id','status','container','reportnum']
        model = DataService

class DataServiceForm(ModelForm):
    cid = forms.CharField(max_length=50,widget=forms.HiddenInput)
    
    class Meta:
        exclude=['id','status','container','reportnum']
        model = DataService

class MFileURLForm(ModelForm):
    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum']
        model = MFile

class MFileForm(ModelForm):
    sid = forms.CharField(max_length=50,widget=forms.HiddenInput)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum']
        model = MFile

class UpdateMFileForm(ModelForm):
    sid = forms.CharField(max_length=50,widget=forms.HiddenInput)

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum']
        model = MFile

class UpdateMFileFormURL(ModelForm):

    class Meta:
        exclude=['name','id','service','mimetype', 'checksum','size','thumb','poster','reportnum']
        model = MFile

class MFileAuthForm(ModelForm):
    dsid = forms.CharField(max_length=50,widget=forms.HiddenInput)
    roles = forms.CharField(max_length=200,label='Roles (comma separated)')
    class Meta:
        exclude=['id','methods_encoded','mfile']
        model = MFileAuth

class SubAuthForm(ModelForm):
    roles_csv = forms.CharField(max_length=200,label='Roles (comma separated)')
    id_parent = forms.CharField(max_length=200,widget=forms.HiddenInput)
    class Meta:
        exclude=['id','methods_encoded']
        model = SubAuth