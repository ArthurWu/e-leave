import sys, os
sys.path.append(r'C:\LeaveSystem\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee
from common.utils import send_email_to_admin, send_mail

def DoCheck():
	reqs = report.CheckNotYetApprovedReqeusts()
	#map(lambda r: r.employee.send_approve_alert_email(r), reqs)
	
	groups = group_reqs(reqs)
	send_email_to(groups)
	
def group_reqs(reqs):
	groups = {}
	for r in reqs:
		emp_name = r.employee.display_name
		if emp_name not in groups:
			groups[emp_name] = [r]
		else:
			groups[emp_name].append(r)
	return groups
	
def send_email_to(groups):
	template = 'maitenance/email//alert_email_list.txt'
	subject = 'Leave Requests - Waiting for manager aproval'
	
	import settings
	host = settings.LEAVESYSTEMHOST or ''
	admin = Employee.objects.filter(is_administrative_staff=True)[0]
	for emp_name, reqs in groups.iteritems():
		c = {'sender': admin.display_name, 'receiver': emp_name, 'reqs': reqs, 'host': host}
		send_mail(template, admin.email, [reqs[0].employee.email], c, subject)

if __name__ == '__main__':
	DoCheck()