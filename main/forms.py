from django import forms
# from .models import CustomUser
from .models import Vehicle
from .models import Smoke

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['file', ]
        widgets = {
            'file': forms.FileInput(
                attrs={'class': 'form-control', 'multiple': False, 'onchange': 'validateFileInput(this)'}),
        }


class SmokeForm(forms.ModelForm):
    class Meta:
        model = Smoke
        fields = ['images', ]  # 修改字段名为 'images'
        widgets = {
            'images': forms.ClearableFileInput(  # 修改字段名为 'images'
                attrs={'class': 'form-control', 'multiple': True, 'onchange': 'validateFileInput(this)', 'name': 'images'}
            ),
        }


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()