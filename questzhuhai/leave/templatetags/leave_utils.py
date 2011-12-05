from django.template import Library
from django import template
import datetime
register = Library()

@register.simple_tag
def period_AM_selected(date):
	if date.time() < datetime.time(12):
		return 'selected="selected"'
	else:
		return ''
	
@register.simple_tag
def period_PM_selected(date):
	if date.time() > datetime.time(12):
		return 'selected="selected"'
	else:
		return ''

def processAction(parser, token):
	try:
		tag_name, employee, leaverequest = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError("%r tag requires two single argument" % token.contents.split()[0])
	return CurrentActions(employee, leaverequest)

from common.logger import log
class CurrentActions(template.Node):
	def __init__(self, employee, leaverequest):
		self.employee = template.Variable(employee)
		self.leaverequest = template.Variable(leaverequest)
		
	def render(self, context):
		try:
			employee = self.employee.resolve(context)
			leavereuqest = self.leaverequest.resolve(context)
			import leave.processe.BaseProcessor as processor
			pro = processor.get_processor(leavereuqest)
			actions = pro.currentStatus.actions
			
			if not employee.is_mine(leavereuqest):
				if actions.has_key('Cancel'): del actions['Cancel']
				if actions.has_key('Edit and Resubmit'): del actions['Edit and Resubmit']
			
			if not employee.is_administrative_staff and actions.has_key('Archive'):
				del actions['Archive']
				
			if not employee.is_approver_of(leavereuqest):
				if actions.has_key('Approve'): del actions['Approve']
				if actions.has_key('Reject'): del actions['Reject']
			
			actions_html = ''
			for k, v in actions.items():
				actions_html += '<a href="%s"  class="actionlink">%s</a>' % (v, k)
				
			return actions_html
		
		except template.VariableDoesNotExist:
			return ''
		
register.tag('process_actions', processAction)