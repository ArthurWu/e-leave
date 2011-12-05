import sys 
sys.path.append(r'C:\LeaveSystem\questzhuhai')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'questzhuhai.settings'

import datetime
from questzhuhai.maitenance.models import Employee
import unittest

class EmployeeTest(unittest.TestCase):
	def length(self):
		self.assertEquals(1,1)
		
	# def test_days_available_of_specify_employee(self):
		# emp = Employee(domain_id='warrior\sheldon',title='',email='',join_date=datetime.datetime(2011,1,1),
				# start_fiscal_date=datetime.datetime(2011,1,1), balanced_forward=0, al_entitlement=12,sl_entitlement=15,approvers='robert',cc_to='andy',
			# )
		# emp.save()
		# emp = Employee.objects.get(domain_id = r'warrior\sheldon')
		# days = emp.days_available()
		# emp.delete()
		# expectation = {u'annual_leave': {'available_days': 11.276712328767124, 'total_days': 11.276712328767124, 'need_approval': 0.0, 'used_days': 0.0}, u'marriage_leave': {'available_days': 13.0, 'total_days': 13, 'need_approval': 0.0, 'used_days': 0.0, 'expire_date': None}, u'bereavement_leave': {'available_days': 3.0, 'total_days': 3, 'need_approval': 0.0, 'used_days': 0.0}, u'sick_leave': {'available_days': 14.095890410958905, 'total_days': 14.095890410958905, 'need_approval': 0.0, 'used_days': 0.0}, u'maternity_leave': {'available_days': 170.0, 'total_days': 170, 'need_approval': 0.0, 'used_days': 0.0}, u'paternity_leave': {'available_days': 10.0, 'total_days': 10, 'need_approval': 0.0, 'used_days': 0.0}}
		
		# self.assertEquals(days, expectation)
		
	