import sys, os
sys.path.append(r'C:\LeaveSystem\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from common import report
from datetime import datetime
from maitenance.models import Employee
from common.utils import send_email_to_admin, send_mail
from common.logger import log

def DoCheck():
	log.Info('Start do alert email check....')
	reqs = report.CheckNotYetApprovedReqeusts()
	#map(lambda r: r.employee.send_approve_alert_email(r), reqs)
	
	groups = group_reqs(reqs)

	log.Info('Groups: ')
	log.Info(groups)

	groups and send_email_to(groups)
	
def group_reqs(reqs):
	def do_group(emp_name, req):
		if emp_name not in groups:
			groups[emp_name] = [req]
		else:
			groups[emp_name].append(req)
	
	groups = {}
	for r in reqs:
		approvers = r.employee.get_approvers()
		for a in approvers:
			do_group(a.display_name+'&'+a.email, r)
		
	return groups
	
def send_email_to(groups):
	template = 'maitenance/email/alert_email_list.txt'
	subject = 'Leave Requests - Waiting for manager aproval'
	
	import settings
	host = settings.LEAVESYSTEMHOST or ''
	admins = Employee.objects.filter(is_administrative_staff=True)#, domain_id='prod\echen1')
	admin = admins and admins[0] or type('', (object,), {'display_name': 'Emily Chen', 'email': 'Emily.Chen@quest.com'})
	
	log.Info('Send Alert Email:')
	for emp_info, reqs in groups.iteritems():
		log.Info('Receiver -- ' + emp_info)
		approver_name, approver_email = emp_info.split('&')
		c = {'sender': admin.display_name, 'receiver': approver_name, 'reqs': reqs, 'host': host}
		
		# For test, add cc to Arthur Wu to confirm that email has been sended.
		send_mail(template, admin.email, [approver_email], c, subject, 
            cc=['Arthur.Wu@quest.com'] + [a.email for a in admins])

if __name__ == '__main__':
	DoCheck()