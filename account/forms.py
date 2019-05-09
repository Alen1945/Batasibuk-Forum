from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import Profile


Male=1
Female=2

class AccountRegisterForm(UserCreationForm):
	email=forms.EmailField()
	info=forms.CharField(max_length=30,required=False)
	date_of_birth=forms.DateField(required=False)
	gender=forms.ChoiceField(choices=(
		(Male,'Pria'),
		(Female,'Wanita')),
		widget=forms.RadioSelect(),
	required=False)
	location=forms.CharField(required=False)
	website=forms.URLField(required=False)

	user_photo=forms.ImageField(required=False)
	# user photo attribut
	x_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	y_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	width_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	height_p=forms.FloatField(widget=forms.HiddenInput(),required=False)



	class Meta:
		model=User
		fields=['username','email','password1','password2',
				'info','date_of_birth','gender','location','website',
				'user_photo','x_p','y_p','width_p','height_p']

	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['username'].widget.attrs={
									'class':'form-control',
									}
		self.fields['username'].label='Username'
		self.fields['email'].widget.attrs={'class':'form-control'}
		self.fields['email'].label='Email'
		self.fields['password1'].widget.attrs={'class':'form-control'}
		self.fields['password1'].label='Password'
		self.fields['password2'].widget.attrs={'class':'form-control'}
		self.fields['password2'].label='Ulangi Password'

		self.fields['info'].label='Info/Status Anda'
		self.fields['info'].widget.attrs={'class':'form-control','data-emojiable':'true'}
		self.fields['info'].initial='Kreator Batasibuk'
		self.fields['gender'].label='Gender'
		self.initial['gender']=Male
		self.fields['gender'].widget.attrs={'class':'form-check-input'}
		self.fields['date_of_birth'].label='Tanggal Lahir'
		self.fields['date_of_birth'].widget.attrs={'class':'form-control'}
		self.fields['location'].label='Lokasi Anda'
		self.fields['location'].widget.attrs={'class':'form-control'}
		self.fields['website'].label='Website'
		self.fields['website'].widget.attrs={'class':'form-control'}
		self.fields['user_photo'].label='Photo'
		self.fields['user_photo'].widget.attrs={'hidden':'true'}

class AccountProfileUpdate(forms.ModelForm):
	# user photo attribut
	date_of_birth=forms.DateField(required=False,widget=forms.DateInput(format='%d-%m-%Y'))
	x_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	y_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	w_p=forms.FloatField(widget=forms.HiddenInput(),required=False)
	h_p=forms.FloatField(widget=forms.HiddenInput(),required=False)

	# user header attribut
	x_h=forms.FloatField(widget=forms.HiddenInput(),required=False)
	y_h=forms.FloatField(widget=forms.HiddenInput(),required=False)
	w_h=forms.FloatField(widget=forms.HiddenInput(),required=False)
	h_h=forms.FloatField(widget=forms.HiddenInput(),required=False)
	class Meta:
		model=Profile
		fields=['info','date_of_birth','location','website',
				'user_photo','x_p','y_p','w_p','h_p',
				'user_header','x_h','y_h','w_h','h_h']
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['date_of_birth'].label='Birthday'
		for f in self.fields.values():
			f.widget.attrs={'class':'form-control'}
		self.fields['info'].widget.attrs={'class':'form-control','data-emojiable':'true'}
		self.fields['user_photo'].widget.attrs={'hidden':'true'}
		self.fields['user_header'].widget.attrs={'hidden':'true'}



class AccountLoginForm(AuthenticationForm):
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['username'].widget.attrs={'class':'form-control'}
		self.fields['username'].label='Username'
		self.fields['password'].widget.attrs={'class':'form-control'}
		self.fields['password'].label='Password'

