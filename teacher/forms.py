from django import forms
from django.contrib.auth.models import User
from . import models
from quiz import models as QMODEL

class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model = models.Teacher
        fields = ['address', 'mobile', 'profile_pic']

class TeacherCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='Select CSV File', help_text='File must contain columns: question, option1, option2, option3, option4, answer, marks')
    course = forms.ModelChoiceField(queryset=QMODEL.Course.objects.all(), label='Select Course')
