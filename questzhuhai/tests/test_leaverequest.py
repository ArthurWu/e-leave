import sys 
sys.path.append(r'C:\LeaveSystem\questzhuhai')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'questzhuhai.settings'

from nose.tools import *
from questzhuhai.maitenance.models import Employee
from questzhuhai.leave.models import *
from questzhuhai.leave.processe import BaseProcessor, status
import datetime

def set_up():
	emp = Employee(domain_id=r'warrior\sheldon',title='',email='',join_date=datetime.datetime(2011,1,1),
			start_fiscal_date=datetime.datetime(2011,1,1), balanced_forward=0, al_entitlement=12,sl_entitlement=15,approvers='robert',cc_to='andy',
		)
	emp.save()
	
def new_leave_request(leaf_type='Annual Leave'):
	emp = Employee.objects.get(domain_id='warrior\sheldon')
	if emp:
		lt = LeaveType.objects.get(name=leaf_type)
		lr = LeaveRequest(employee=emp, leave_type=lt)
		lr.save()
		return lr
	else:
		return None
	
def get_leave_request(id):
	return LeaveRequest.objects.get(id=id)
	
def test_new_leave_request():
	set_up()
	
	lr = new_leave_request()
	assert_equals(lr is not None, True)
	
	tear_down()
	
def test_annual_leave_processe1():
	set_up()
	
	lr = new_leave_request()
	pro = BaseProcessor.get_processor(lr)
	pro.submit()
	assert_equals(lr.status, status.PENDINGMANAGER)
	
	pro = BaseProcessor.get_processor(lr)
	pro.reject()
	assert_equals(lr.status, status.PENDINGEMPLOYEE)
	
	pro = BaseProcessor.get_processor(lr)
	pro.resubmit()
	assert_equals(lr.status, status.PENDINGMANAGER)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.archive()
	assert_equals(lr.status, status.ARCHIVED)
	
	tear_down()
	
def test_annual_leave_processe2():
	set_up()
	
	lr = new_leave_request()
	pro = BaseProcessor.get_processor(lr)
	pro.submit()
	assert_equals(lr.status, status.PENDINGMANAGER)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.cancel()
	assert_equals(lr.status, status.CANCELED)
	
	tear_down()
	
def test_maital_leave_processe():
	set_up()
	
	lr = new_leave_request('Marital Leave')
	pro = BaseProcessor.get_processor(lr)
	pro.submit()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGMANAGER)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.archive()
	assert_equals(lr.status, status.ARCHIVED)
	
	tear_down()
	
def test_maital_leave_processe_cancel():
	set_up()
	
	lr = new_leave_request('Marital Leave')
	pro = BaseProcessor.get_processor(lr)
	pro.submit()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.reject()
	assert_equals(lr.status, status.PENDINGEMPLOYEE)
	
	pro = BaseProcessor.get_processor(lr)
	pro.resubmit()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGMANAGER)
	
	pro = BaseProcessor.get_processor(lr)
	pro.approve()
	assert_equals(lr.status, status.PENDINGADMIN)
	
	pro = BaseProcessor.get_processor(lr)
	pro.cancel()
	assert_equals(lr.status, status.CANCELED)
	
	tear_down()
	
def tear_down():
	emp = Employee.objects.get(domain_id=r'warrior\sheldon')
	if emp: emp.delete()