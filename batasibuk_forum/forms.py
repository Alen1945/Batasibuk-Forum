from django import forms
from .models import Post


class NewPostForm(forms.ModelForm):
	class Meta:
		model=Post
		fields=['forum','post_title','body']
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['post_title'].widget.attrs={'class':'form-control','placeholder':'Masukan Judul'}
		self.fields['post_title'].label="Judul"
		self.fields['body'].label="Detail"
