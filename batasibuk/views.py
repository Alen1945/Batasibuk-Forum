from django.views.generic import TemplateView


class index(TemplateView):
	template_name='home.html'
	def get_context_data(self,*args,**kwargs):
		context={
			'title':'Home'
		}
		return context