from django import forms
from .fields import ListTextWidget
from .models import (Forum,SubForum,Post,Comment)

class NewPostForm(forms.ModelForm):
	select_forum=forms.ChoiceField(required=True,choices=[])
	class Meta:
		model=Post
		fields=['select_forum','post_title','body']
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		choices=[]
		for forum in Forum.objects.all():
			choices.append((f'fr-{forum.id}',forum.name))
			if forum.subforums.all():
				for subforum in forum.subforums.all():
					choices.append((f'sfr-{subforum.id}',subforum.name))
		self.fields['select_forum'].choices=choices
		self.fields['post_title'].widget.attrs={'class':'form-control','placeholder':'Masukan Judul'}
		self.fields['post_title'].label="Judul"
		self.fields['body'].label="Detail"
		self.fields['body'].widget.attrs={'class':'form-control','style':'width:100%;'}
		self.fields['select_forum'].label='Forum'
		self.fields['select_forum'].widget.attrs={'class':'selectpicker','data-live-search':'true'}
class NewCommentForm(forms.ModelForm):
	class Meta:
		model=Comment
		fields=['body']
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.fields['body'].widget.attrs={'class':'form-control','placeholder':'Berikan Komentar untuk Thread ini'}

