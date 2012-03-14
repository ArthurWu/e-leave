from status import *
from leave.models import LeaveType

class BaseProcessor(object):
	
	def __init__(self, leaveRequest, employee):
		self.leaverequest = leaveRequest
		self.employee = employee
		self.status = {
			INITIAL: Initial(leaveRequest, employee),
			PENDINGMANAGER: PendingManager(leaveRequest, employee),
			WAITINGADMINCONFIRM: WaitingAdminConfirm(leaveRequest, employee),
			PENDINGADMIN: PendingAdmin(leaveRequest, employee),
			PENDINGEMPLOYEE: PendingEmployee(leaveRequest, employee),
			ARCHIVED: Archived(leaveRequest, employee),
			CANCELED: Canceled(leaveRequest, employee)
		}
		status_str = self.leaverequest.status
		if not self.leaverequest.status:
			status_str = INITIAL
		self.currentStatus = self.status[status_str]
		
	def submit(self):
		self.currentStatus.submit()
		
	def edit(self):
		return self.currentStatus.edit()
		
	def approve(self):
		return self.currentStatus.approve()
		
	def reject(self, reason=''):
		return self.currentStatus.reject(reason)
		
	def resubmit(self):
		return self.currentStatus.resubmit()
		
	def archive(self):
		return self.currentStatus.archive()
		
	def cancel(self):
		return self.currentStatus.cancel()
		
	def actions(self):
		roles = []
		if self.employee.is_mine(self.leaverequest):
			roles.append('owner')
		if self.employee.is_approver_of(self.leaverequest):
			roles.append('approver')
		if self.employee.is_administrative_staff:
			roles.append('admin')
	
		return self.currentStatus.get_actions(roles)
		
		
class AnnualLeaveProcessor(BaseProcessor):
	def __init__(self, leaveRequest, employee):
		super(AnnualLeaveProcessor, self).__init__(leaveRequest, employee)
		
		self.status[INITIAL].afterSubmit = PENDINGMANAGER
		self.status[PENDINGMANAGER].afterApprove = PENDINGADMIN
		self.status[PENDINGMANAGER].afterReject = PENDINGEMPLOYEE
		
		self.status[PENDINGEMPLOYEE].afterResubmit = PENDINGMANAGER
		self.status[PENDINGMANAGER].afterResubmit = PENDINGMANAGER
		#self.status[PENDINGADMIN].afterResubmit = PENDINGMANAGER
		self.status[WAITINGADMINCONFIRM].afterResubmit = PENDINGMANAGER
		
		self.status[PENDINGADMIN].afterArchive = ARCHIVED
		
		self.status[INITIAL].afterCancel = CANCELED
		self.status[PENDINGMANAGER].afterCancel = CANCELED
		self.status[PENDINGEMPLOYEE].afterCancel = CANCELED
		self.status[PENDINGADMIN].afterCancel = CANCELED
		
		
class AdminConfirmLeaveProcessor(BaseProcessor):
	def __init__(self, leaveRequest, employee):
		super(AdminConfirmLeaveProcessor, self).__init__(leaveRequest, employee)
		
		self.status[INITIAL].afterSubmit = WAITINGADMINCONFIRM
		self.status[WAITINGADMINCONFIRM].afterApprove = PENDINGMANAGER
		self.status[WAITINGADMINCONFIRM].afterReject = PENDINGEMPLOYEE
		self.status[PENDINGEMPLOYEE].afterResubmit = WAITINGADMINCONFIRM
		self.status[WAITINGADMINCONFIRM].afterResubmit = WAITINGADMINCONFIRM
		self.status[PENDINGMANAGER].afterResubmit = WAITINGADMINCONFIRM
		#self.status[PENDINGADMIN].afterResubmit = WAITINGADMINCONFIRM
		self.status[PENDINGMANAGER].afterApprove = PENDINGADMIN
		self.status[PENDINGMANAGER].afterReject = PENDINGEMPLOYEE
		self.status[PENDINGADMIN].afterArchive = ARCHIVED
		
		self.status[INITIAL].afterCancel = CANCELED
		self.status[WAITINGADMINCONFIRM].afterCancel = CANCELED
		self.status[PENDINGMANAGER].afterCancel = CANCELED
		self.status[PENDINGEMPLOYEE].afterCancel = CANCELED
		self.status[PENDINGADMIN].afterCancel = CANCELED

def available_processors():
	need_notify_admin_types = LeaveType.objects.filter(notifyadmin = True)
	other_types = LeaveType.objects.filter(notifyadmin = False)
	processors = {}
	for i in need_notify_admin_types:
		processors[i.name] = AdminConfirmLeaveProcessor
	for i in other_types:
		processors[i.name] = AnnualLeaveProcessor
	return processors

def get_processor(leaveRequest, employee=None):
	processors = available_processors()
	if processors.has_key(leaveRequest.leave_type.name):
		return processors[leaveRequest.leave_type.name](leaveRequest, employee)
	else:
		return processors['Annual Leave'](leaveRequest, employee)