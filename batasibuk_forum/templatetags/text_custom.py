from batasibuk.utils.time_since import custom_time_since
from django import template

register=template.Library()


@register.filter(name='to_time_since')
def to_time_since(d):
	return custom_time_since(d)