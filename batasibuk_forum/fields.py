from django import forms

class ListTextWidget(forms.TextInput):
	def __init__(self,data_list,name,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self._name=name
		self._list=data_list
		self.attrs.update({'list':f'list_{self._name}'})

	def render(self,name,value,attrs=None,renderer=None):
		text_html=super().render(name,value,attrs=attrs,renderer=None)
		data_list=f'<datalist id="list_{self._name}">'
		for item in self._list:
			data_list+=f'<option value="{item[0]}">{item[1]}</option>'
		data_list+='</datalist>'
		return (text_html+data_list)
