from django import forms
from django.contrib.auth.models import User
from . import models
from quiz import models as QMODEL

class StudentUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
            'password': forms.PasswordInput()
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model=models.Student
        fields=['address','mobile','profile_pic']

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select CSV File', help_text='File must contain columns: question,option1,option2,option3,option4,answer')
    course = forms.ModelChoiceField(queryset=QMODEL.Course.objects.all(), label='Select Course')
