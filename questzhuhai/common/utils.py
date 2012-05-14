import smtplib
from email.mime.text import MIMEText
from django.template.loader import get_template
from django.template import Context
from maitenance.models import Employee
from ConfigParser import RawConfigParser
import os

resFilePath = os.path.join(os.path.dirname(__file__), "res.conf")

def mait_path():
	return os.path.join(os.path.dirname(__file__), "../maitenance")

def resfile():
	return fullpath(mait_path(), 'res.conf')
	
def fullpath(path, filename):
	return os.path.join(path, filename)

def read(path, section, key):
	conf = RawConfigParser()
	conf.read(path)
	return conf.get( section, key )
	
def write(path, section, key, value):
	conf = RawConfigParser()
	conf.read(path)
	conf.set( section, key, value )
	configfile = open(path, 'w')
	conf.write(configfile)
	configfile.close()

def send_mail(template, sender, receivers, context=None, subject='Email From E-Leave System', cc=None):	
	t = get_template(template)
	email_text = t.render(Context(context or {}))

	msg = MIMEText(email_text)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = ', '.join(receivers)
	msg['CC'] = ', '.join(cc or [])
	
	s = smtplib.SMTP('10.1.0.160')
	s.sendmail(sender, receivers, msg.as_string())
	s.quit()
	
def send_email_to_admin(template_name, subject, end_date, start_date=None, type="leave report"):
	admins = Employee.objects.filter(is_administrative_staff=True, is_active=True)
	tolist = [a.email for a in admins]
	from_addr = tolist[0] if tolist else None

	import settings
	host = settings.LEAVESYSTEMHOST or ''
	
	if type == 'leave report':
		link = '/eleave/main/reports/download/leavereport/%s' % end_date.strftime('%Y/%m/%d/')
	else:
		link = '/eleave/main/reports/download/leaverecord/%s/%s/' % \
				(start_date.strftime('%Y_%m_%d'), end_date.strftime('%Y_%m_%d'))
	
	c = {'end_date': end_date, 'host': host, 'link': link, 'start_date': start_date, 'type': type}
	import common.report as report
	notApprovedReqs = report.GetNoeApprovedInReportMonth(start_date, end_date)
	c['not_approved_reqs'] = notApprovedReqs or None
	
	template_path = 'maitenance/email/'
	send_mail(template = template_path+template_name,
				sender = from_addr,
				receivers = tolist,
				context = c,
				subject = subject)