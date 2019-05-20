import datetime
import calendar

from django.utils.html import avoid_wrapping
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext, ngettext_lazy


def custom_time_since(d):
	time_strings = {
	'year': ngettext_lazy('%d year', '%d years'),
	'month': ngettext_lazy('%d month', '%d months'),
	'week': ngettext_lazy('%d week', '%d weeks'),
	'day': ngettext_lazy('%d day', '%d days'),
	'hour': ngettext_lazy('%d hour', '%d hours'),
	'minute': ngettext_lazy('%d minute', '%d minutes'),
	}

	TIMESINCE_CHUNKS = (
	    (60 * 60 * 24 * 365, 'year'),
	    (60 * 60 * 24 * 30, 'month'),
	    (60 * 60 * 24 * 7, 'week'),
	    (60 * 60 * 24, 'day'),
	    (60 * 60, 'hour'),
	    (60, 'minute'),
	)


	if not isinstance(d, datetime.datetime):
	    d = datetime.datetime(d.year, d.month, d.day)

	now =datetime.datetime.now(utc if is_aware(d) else None)

	delta = now - d


	leapdays = calendar.leapdays(d.year, now.year)
	if leapdays != 0:
	    if calendar.isleap(d.year):
	        leapdays -= 1
	    elif calendar.isleap(now.year):
	        leapdays += 1
	delta -= datetime.timedelta(leapdays)

	since = delta.days * 24 * 60 * 60 + delta.seconds
	if since <= 59:
	    result=f'{since} detik'
	    return result +' yang lalu'
	for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
	    count = since // seconds
	    if count != 0:
	        break
	if i<=2:
		return d.strftime('%d %B,%Y')
	result = time_strings[name] % count
	return result +' yang lalu'
