from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm



class AccountRegisterForm(UserCreationForm):
	email=forms.EmailField()
	error_messages={
	'password_mismatch':'Password yang dimasukan harus sama',
	}
	class Meta:
		model=User
		fields=['username','email','password1','password2']
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['username'].widget.attrs={
									'class':'form-control',
									'placeholder':'Masukan Nama Anda'
									}
		self.fields['username'].label='Username'
		self.fields['email'].widget.attrs={'class':'form-control','placeholder':'Masukan Email Anda'}
		self.fields['email'].label='Email'
		self.fields['password1'].widget.attrs={'class':'form-control','placeholder':'Masukan Passoword Anda'}
		self.fields['password1'].label='Password'
		self.fields['password2'].widget.attrs={'class':'form-control','placeholder':'Ulangi Lagi'}
		self.fields['password2'].label='Password Confirm'
	def clean_username(self):
		username=self.cleaned_data.get('username')
		if User.objects.filter(username=self.cleaned_data.get('username')):
			raise forms.ValidationError('Nama sudah terdaftar, coba yang lain')
		return username

class AccountLoginForm(AuthenticationForm):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['username'].widget.attrs={'class':'form-control','placeholder':'Masukan Username'}
		self.fields['password'].widget.attrs={'class':'form-control','placeholder':'Masukan Password'}