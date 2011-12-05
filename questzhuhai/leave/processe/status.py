from django.core import mail
import smtplib
from email.mime.text import MIMEText
from django.template import Template, Context, loader
from django.core.urlresolvers import reverse
from maitenance.models import Employee


INITIAL = 'New leave request'
PENDINGMANAGER = 'Waiting for manager approval'
WAITINGADMINCONFIRM = 'Waiting for Admin confirmation'
PENDINGADMIN = 'Approved'
PENDINGEMPLOYEE = 'Rejected'
ARCHIVED = 'Archived'
CANCELED = 'Canceled'

class BaseStatus(object):
	name = ''
	afterSubmit = ''
	afterResubmit = ''
	afterApprove = ''
	afterReject = ''
	afterArchive = ''
	afterCancel = ''
	
	email_template = ''
	receiver = None
	cc_to = ''
	
	
	def __init__(self, leaveRequest, employee, name='base status'):
		self.leaveRequest = leaveRequest
		self.employee = employee
		self.name = name
		self.reason = ''
		self.email_subject = subject = '[' + self.leaveRequest.leave_type.name + '] request - ' + self.leaveRequest.employee.display_name
		self.is_cancel = False
		self.is_approve = False
		self.is_resubmit = False
		self.is_edit = False
		
		self.actionList = {
			'owner': {
				'Cancel': reverse('leave_request_cancel', args=[self.leaveRequest.id]),
				'Edit': reverse('leave_request_edit', args=[self.leaveRequest.id])
			},
			'approver': {
				'Approve': reverse('leave_request_approve', args=[self.leaveRequest.id]),
				'Reject': reverse('leave_request_reject', args=[self.leaveRequest.id]),
			},
			'admin': {
				'Archive': reverse('leave_request_archive', args=[self.leaveRequest.id])
			},
			'none': {}
		}
		
	def get_actions(self, roles):		
		actions = {}
		for role in roles:
			if role == 'owner' and not self.leaveRequest.is_approved():
				actions.update(self.actionList['owner'])
			if role == 'approver':
				if self.leaveRequest.status not in (ARCHIVED, CANCELED):
					actions.update(self.actionList['owner'])
				if self.leaveRequest.status == PENDINGMANAGER:
					actions.update(self.actionList['approver'])
			if role == 'admin':
				if self.leaveRequest.status not in (ARCHIVED, CANCELED):
					actions.update(self.actionList['owner'])
				if self.leaveRequest.status == WAITINGADMINCONFIRM:
					actions.update(self.actionList['approver'])
				if self.leaveRequest.status == PENDINGADMIN:
					actions.update(self.actionList['admin'])
		return actions
	
	def _have_actions(self, role):
		return (role == 'owner' and not self.leaveRequest.is_approved()) or \
				(role == 'approver') or \
				(role == 'admin' and self.leaveRequest.status == PENDINGADMIN)
		
	def _change_status(self, status):
		self.leaveRequest.status = status
		self.leaveRequest.save()
	
	def send_email(self):
		pass
	
	def submit(self):
		self._change_status(self.afterSubmit)
		self.send_email()
	
	def edit(self):
		self.is_edit = True
		self.send_email()
	
	def approve(self):
		self.is_approve = True
		self._change_status(self.afterApprove)
		self.send_email()
		
	def reject(self, reason=''):
		self.reason = reason
		self.is_approve = False
		self._change_status(self.afterReject)
		self.send_email()
		
	def resubmit(self):
		self.is_resubmit = True
		self._change_status(self.afterResubmit)
		self.send_email()
		
	def archive(self):
		self._change_status(self.afterArchive)
		self.send_email()
		
	def cancel(self):
		self.is_cancel = True
		self._change_status(self.afterCancel)
		self.send_cancel_email()
		
	def _send_email(self, tolist, cc, subject, template_name):
		from_addr = self.employee.email
		t = loader.get_template(template_name)
		
		import settings
		host = settings.LEAVESYSTEMHOST or ''
		
		c = Context({'employee': self.leaveRequest.employee, 'leaverequest': self.leaveRequest, 'reason': self.reason, 'host': host, 'operator': self.employee})
		email_text = t.render(c)
		
		msg = MIMEText(email_text)
		msg['Subject'] = subject
		msg['From'] = from_addr
		msg['To'] = ', '.join(tolist)
		msg['CC'] = ', '.join(cc)
		
		s = smtplib.SMTP('10.1.0.160')
		s.sendmail(from_addr, tolist + cc, msg.as_string())
		s.quit()
		
	def send_cancel_email(self):
		tolist, cc = self._edit_cancel_emails()
		subject = self.email_subject + ' - Canceled'
		self._send_email(tolist, cc, subject, 'leave/email/cancel.txt')
	
	def send_resubmit_email(self):
		tolist, cc = self._edit_cancel_emails()
		subject = self.email_subject + ' - Edited'
		self._send_email(tolist, cc, subject, 'leave/email/resubmit.txt')
	
	def _edit_cancel_emails(self):
		emp = self.employee
		tolist = emp.approvers_email() 
		cc = emp.cc_to_email() + [emp.email] + admin_emails()
		
		manager = self.employee.is_approver_of(self.leaveRequest)
		admin = self.employee.is_administrative_staff
		if manager or admin:
			tolist = [self.leaveRequest.employee.email]
			cc = [self.employee.email] + admin_emails() \
				+ self.leaveRequest.employee.cc_to_email() \
				+ self.leaveRequest.employee.approvers_email()
		return tolist, cc
	
def admin_emails():
	admins = Employee.objects.filter(is_administrative_staff=True)
	cc = [a.email for a in admins]
	return cc
		
class Initial(BaseStatus):
	def __init__(self, leaveRequest, employee, name=INITIAL):
		super(Initial, self).__init__(leaveRequest, employee, name)
	
	# submit: email to approver, and cc to self and administrative staff 
	def send_email(self):
		tolist = self.employee.approvers_email()
		cc = self.employee.cc_to_email() + [self.employee.email]
		self._send_email(tolist, cc, self.email_subject, 'leave/email/submit.txt')

class PendingManager(BaseStatus):
	def __init__(self, leaveRequest, employee, name=PENDINGMANAGER):
		super(PendingManager, self).__init__(leaveRequest, employee, name)
		
	def get_template_and_subject():
		if self.is_approve:
			template = 'leave/email/approve.txt'
			subject = self.email_subject + ' - Approved'
		elif self.is_edit:
			template = 'leave/email/edit.txt'
			subject = self.email_subject + ' - Edited'
		else:
			template = 'leave/email/reject.txt'
			subject = self.email_subject + ' - Rejected'
			
		return template, subject
	
	def send_email(self):
		if self.is_cancel:
			self.send_cancel_email()
		elif self.is_resubmit:
			self.send_resubmit_email()
		else:
			template, subject = self.get_template_and_subject()
			tolist = [self.leaveRequest.employee.email]
			cc = admin_emails() + [self.employee.email]
			self._send_email(tolist, cc, subject, template)
		
class WaitingAdminConfirm(PendingManager):
	def __init__(self, leaveRequest, employee, name=WAITINGADMINCONFIRM):
		super(WaitingAdminConfirm, self).__init__(leaveRequest, employee, name)
		
	def get_template_and_subject():
		if self.is_approve:
			template = 'leave/email/admin_confirm.txt'
			subject = self.email_subject + ' - Admin confirmed'
		elif self.is_edit:
			template = 'leave/email/edit.txt'
			subject = self.email_subject + ' - Edited'
		else:
			template = 'leave/email/reject.txt'
			subject = self.email_subject + ' - Rejected'
			
		return template, subject

class PendingAdmin(BaseStatus):
	def __init__(self, leaveRequest, employee, name=PENDINGADMIN):
		super(PendingAdmin, self).__init__(leaveRequest, employee, name)
		
	def send_email(self):
		if self.is_cancel:
			self.send_cancel_email()
		elif self.is_resubmit:
			self.send_resubmit_email()
				
class PendingEmployee(Initial):
	def __init__(self, leaveRequest, employee, name=PENDINGEMPLOYEE):
		super(PendingEmployee, self).__init__(leaveRequest, employee, name)
	
	def send_email(self):
		if self.is_cancel:
			self.send_cancel_email()
		else:
			super(PendingEmployee, self).send_email()
		
class Archived(BaseStatus):
	def __init__(self, leaveRequest, employee, name=ARCHIVED):
		super(Archived, self).__init__(leaveRequest, employee, name)
		
class Canceled(BaseStatus):
	def __init__(self, leaveRequest, employee, name=CANCELED):
		super(Canceled, self).__init__(leaveRequest, employee, name)
		
		