import sys, os
sys.path.append(r'C:\projects\questzhuhai')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from maitenance.models import *
from leave.models import *

sheldon = Employee.objects.get(id=1)		#admin
administrator = Employee.objects.get(id=2)
peter = Employee.objects.get(id=3)
infoportaladmin = Employee.objects.get(id=4)
arthur = Employee.objects.get(id=5)
jimmy = Employee.objects.get(id=6)
tony = Employee.objects.get(id=7)
lina = Employee.objects.get(id=8)
andy = Employee.objects.get(id=9)

annual_leave = LeaveType.objects.get(id=1)
sick_leave = LeaveType.objects.get(id=2)
marriage_leave = LeaveType.objects.get(id=3)
maternity_leave = LeaveType.objects.get(id=4)
paternity_leave = LeaveType.objects.get(id=5)
bereavement_leave = LeaveType.objects.get(id=6)

def clear_leave_quest_data():
	emps = [sheldon, administrator, peter, infoportaladmin, arthur, jimmy, tony, lina, andy]
	for e in emps:
		e.leaverequest_set.all().delete()

def prepare_leave_request_data():
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=annual_leave, days=1)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,8,10,9),end=datetime.datetime(2011,8,10,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=annual_leave, days=3)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,9,10,9),end=datetime.datetime(2011,9,12,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=annual_leave, days=2)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,25,9),end=datetime.datetime(2011,11,25,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,28,9),end=datetime.datetime(2011,11,28,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=sick_leave, days=4)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,5,24,9),end=datetime.datetime(2011,5,27,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=marriage_leave, days=13)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,7,1,9),end=datetime.datetime(2011,7,5,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,7,8,9),end=datetime.datetime(2011,7,12,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,7,15,9),end=datetime.datetime(2011,7,17,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=paternity_leave, days=10)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,8,9),end=datetime.datetime(2011,11,11,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,14,9),end=datetime.datetime(2011,11,18,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,21,9),end=datetime.datetime(2011,11,21,13))
	
	leave_request = LeaveRequest.objects.create(employee=peter, status="Approved",leave_type=bereavement_leave, days=3)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,7,9),end=datetime.datetime(2011,12,9,13))
	
	leave_request = LeaveRequest.objects.create(employee=jimmy, status="Approved",leave_type=annual_leave, days=3)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,1,10,9),end=datetime.datetime(2011,1,10,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,1,15,9),end=datetime.datetime(2011,1,15,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,1,21,9),end=datetime.datetime(2011,1,21,13))
	
	leave_request = LeaveRequest.objects.create(employee=jimmy, status="Approved",leave_type=annual_leave, days=3)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,8,10,9),end=datetime.datetime(2011,8,10,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,8,19,9),end=datetime.datetime(2011,8,19,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,8,31,9),end=datetime.datetime(2011,8,31,13))
	
	leave_request = LeaveRequest.objects.create(employee=jimmy, status="Approved",leave_type=paternity_leave, days=10)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,12,9),end=datetime.datetime(2011,12,16,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,19,9),end=datetime.datetime(2011,12,23,13))
	
	leave_request = LeaveRequest.objects.create(employee=lina, status="Approved",leave_type=maternity_leave, days=153)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,4,1,9),end=datetime.datetime(2011,8,31,13))
	
	leave_request = LeaveRequest.objects.create(employee=andy, status="Approved",leave_type=marriage_leave, days=10)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,1,9),end=datetime.datetime(2011,12,2,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,5,9),end=datetime.datetime(2011,12,9,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,12,12,9),end=datetime.datetime(2011,12,14,13))
	
	leave_request = LeaveRequest.objects.create(employee=arthur, status="Approved",leave_type=annual_leave, days=1.5)
	Period.objects.create(leave_request=lr3, start=datetime.datetime(2011,8,23,9),end=datetime.datetime(2011,8,23,13))
	Period.objects.create(leave_request=lr3, start=datetime.datetime(2011,8,26,9),end=datetime.datetime(2011,8,26,9))
	
	leave_request = LeaveRequest.objects.create(employee=tony, status="Approved",leave_type=annual_leave, days=4)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,9,8,9),end=datetime.datetime(2011,9,9,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,9,12,9),end=datetime.datetime(2011,9,13,13))
	
	leave_request = LeaveRequest.objects.create(employee=infoporataladmin, status="Approved",leave_type=sick_leave, days=5)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,10,24,9),end=datetime.datetime(2011,10,26,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,10,27,9),end=datetime.datetime(2011,10,27,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,25,9),end=datetime.datetime(2011,11,25,13))
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,11,27,9),end=datetime.datetime(2011,11,27,13))
	
	leave_request = LeaveRequest.objects.create(employee=arthur, status="Approved",leave_type=annual_leave, days=1)
	Period.objects.create(leave_request=leave_request, start=datetime.datetime(2011,8,10,9),end=datetime.datetime(2011,8,10,13))
	
if __name__ == '__main__':
	args = sys.args[1:]
	if not args:
		print 'Please input a command(-c => clear test data; -p => prepare test data)'
	else:
		if args[0] == '-c':
			clear_leave_quest_data()
		elif args[0] == '-p':
			prepare_leave_request_data()
		else:
			print "'%s' is not recognizated as a command."