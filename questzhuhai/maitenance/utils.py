import smtplib
from email.mime.text import MIMEText
from django.template.loader import get_template
from django.template import Context
import main_utils
from models import Employee

def send_email_to_admin(template_name, subject, end_date, start_date=None, type="leave report"):
	admins = Employee.objects.filter(is_administrative_staff=True, is_active=True)
	tolist = [a.email for a in admins]
	from_addr = tolist[0] if tolist else None
	
	t = get_template(template_name)
	
	import settings
	host = settings.LEAVESYSTEMHOST or ''
	
	if type == 'leave report':
		link = '/main/reports/download/leavereport/%s' % end_date.strftime('%Y/%m/%d/')
	else:
		link = '/main/reports/download/leaverecord/%s/%s/' % \
				(start_date.strftime('%Y_%m_%d'), end_date.strftime('%Y_%m_%d'))
	
	c = Context({'end_date': end_date, 'host': host, 'link': link, 'start_date': start_date, 'type': type})
	email_text = t.render(c)
	
	msg = MIMEText(email_text)
	msg['Subject'] = subject
	msg['From'] = from_addr
	msg['To'] = ', '.join(tolist)
	
	s = smtplib.SMTP('10.1.0.160')
	s.sendmail(from_addr, tolist, msg.as_string())
	s.quit()