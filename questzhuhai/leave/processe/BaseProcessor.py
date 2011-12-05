from status import *

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
		self.currentStatus = self.status[self.leaverequest.status]
		
	def submit(self):
		self.currentStatus.submit()
		
	def edit(self):
		self.currentStatus.edit()
		
	def approve(self):
		self.currentStatus.approve()
		
	def reject(self, reason=''):
		self.currentStatus.reject(reason)
		
	def resubmit(self):
		self.currentStatus.resubmit()
		
	def archive(self):
		self.currentStatus.archive()
		
	def cancel(self):
		self.currentStatus.cancel()
		
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
		self.status[PENDINGADMIN].afterResubmit = PENDINGMANAGER
		self.status[PENDINGADMIN].afterArchive = ARCHIVED
		
		self.status[INITIAL].afterCancel = CANCELED
		self.status[PENDINGMANAGER].afterCancel = CANCELED
		self.status[PENDINGEMPLOYEE].afterCancel = CANCELED
		self.status[PENDINGADMIN].afterCancel = CANCELED
		
		
class MaritalLeaveProcessor(BaseProcessor):
	def __init__(self, leaveRequest, employee):
		super(MaritalLeaveProcessor, self).__init__(leaveRequest, employee)
		
		self.status[INITIAL].afterSubmit = WAITINGADMINCONFIRM
		self.status[WAITINGADMINCONFIRM].afterApprove = PENDINGMANAGER
		self.status[WAITINGADMINCONFIRM].afterReject = PENDINGEMPLOYEE
		self.status[PENDINGEMPLOYEE].afterResubmit = WAITINGADMINCONFIRM
		self.status[WAITINGADMINCONFIRM].afterResubmit = WAITINGADMINCONFIRM
		self.status[PENDINGMANAGER].afterResubmit = WAITINGADMINCONFIRM
		self.status[PENDINGADMIN].afterResubmit = WAITINGADMINCONFIRM
		self.status[PENDINGMANAGER].afterApprove = PENDINGADMIN
		self.status[PENDINGMANAGER].afterReject = PENDINGEMPLOYEE
		self.status[PENDINGADMIN].afterArchive = ARCHIVED
		
		self.status[INITIAL].afterCancel = CANCELED
		self.status[WAITINGADMINCONFIRM].afterCancel = CANCELED
		self.status[PENDINGMANAGER].afterCancel = CANCELED
		self.status[PENDINGEMPLOYEE].afterCancel = CANCELED
		self.status[PENDINGADMIN].afterCancel = CANCELED
		
processors = {
	'Annual Leave': AnnualLeaveProcessor,
	'Marriage Leave': MaritalLeaveProcessor,
	'Sick Leave': AnnualLeaveProcessor,
	'Maternity Leave': MaritalLeaveProcessor,
	'Bereavement Leave': MaritalLeaveProcessor
}

def get_processor(leaveRequest, employee=None):
	if processors.has_key(leaveRequest.leave_type.name):
		return processors[leaveRequest.leave_type.name](leaveRequest, employee)
	else:
		return processors['Annual Leave'](leaveRequest, employee)