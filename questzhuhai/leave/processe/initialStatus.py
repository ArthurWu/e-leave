from status import BaseStatus

class InitialStatus(BaseStatus):
	name  = 'initial'
	actions = ('submit',)
	
	def submit(self):
		