import sys 
sys.path.append(r'C:\LeaveSystem\questzhuhai')
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'questzhuhai.settings'

from nose.tools import *
from questzhuhai.maitenance import main_utils, resource

def test_get_all_admins():
	result1 = main_utils.add_admin(r'warrior\administrator', 'art')
	result2 = main_utils.add_admin(r'warrior\peter', 'art')
	result3 = main_utils.add_admin(r'warrior\admin', 'art')
	
	assert_equals(result1['error'], '')
	assert_equals(result2['error'], '')
	assert_equals(result3['error'], resource.user_not_exist % r'warrior\admin')
	
	admins  = main_utils.get_all_admins()
	assert_equals(len(admins['data']), 2)
	
	main_utils.delete_admin(r'warrior\administrator', 'art')
	main_utils.delete_admin(r'warrior\peter', 'art')
	
	admins_after  = main_utils.get_all_admins()
	assert_equals(len(admins_after['data']), 0)

	
def test_leave_type_adsc():
	type1 = main_utils.add_leave_type('Sick', 'Andy')
	
	assert_equals(type1['error'], '')
	assert_equals(type1['data'].name, 'Sick')
	assert_equals(type1['data'].notifyadmin, False)
	
	leaveTypes = main_utils.get_all_leave_types()
	assert_equals(leaveTypes['error'], '')
	assert_equals(len(leaveTypes['data']), 1)
	
	
	type2 = main_utils.update_leave_type(type1['data'].id, True, "Andy")
	
	assert_equals(type2['error'], '')
	assert_equals(type2['data'].name, 'Sick')
	assert_equals(type2['data'].notifyadmin, True)
	
	#res = main_utils.delete_leave_type(type2['data'].id,"Andy")
	
	# assert_equals(res['error'], '')
	
	# leaveTypes = main_utils.get_all_leave_types()
	# assert_equals(leaveTypes['error'], '')
	# assert_equals(len(leaveTypes['data']), 0)
	
def test_department_adsc():
	dep1 = main_utils.add_department('Windows Management', 'Andy')
	
	assert_equals(dep1['error'], '')
	assert_equals(dep1['data'].name, 'Windows Management')
	
	
	deps = main_utils.get_all_departments()
	assert_equals(deps['error'], '')
	assert_equals(len(deps['data']), 1)

	
	res = main_utils.delete_department(dep1['data'].id,"Andy")
	
	assert_equals(res['error'], '')
	
	deps = main_utils.get_all_departments()
	assert_equals(deps['error'], '')
	assert_equals(len(deps['data']), 0)
	
def test_team_adsc():
	dep1 = main_utils.add_department('Windows Management', 'Andy')
	dep2 = main_utils.add_department('Database Management', 'Andy')
	
	assert_equals(dep1['error'], '')
	assert_equals(dep1['data'].name, 'Windows Management')
	
	
	deps = main_utils.get_all_departments()
	assert_equals(deps['error'], '')
	assert_equals(len(deps['data']), 2)

	team1 = main_utils.add_team(dep1['data'].id, "Site Administrator for SharePoint", 'Andy')
	team2 = main_utils.add_team(dep1['data'].id, "Archive Manager", 'Andy')
	
	teams = main_utils.get_teams_by_department(dep1['data'].id)
	
	assert_equals(teams['error'], '')
	assert_equals(len(teams['data']), 2)
	
	res = main_utils.delete_team(team1['data'].id, "Andy")
	
	assert_equals(res['error'], '')
	
	teams = main_utils.get_teams_by_department(dep1['data'].id)
	
	assert_equals(teams['error'], '')
	assert_equals(len(teams['data']), 1)
	
	res = main_utils.delete_department(dep1['data'].id,"Andy")
	
	assert_equals(res['error'], '')
	
	res = main_utils.delete_department(dep2['data'].id,"Andy")
	
	assert_equals(res['error'], '')
	
	deps = main_utils.get_all_departments()
	assert_equals(deps['error'], '')
	assert_equals(len(deps['data']), 0)
	
def test_import_employees():
	res = main_utils.add_employees(r'employees.xls','andy')
	assert_equals(res, '')
	
def test_handle_uploaded_file():
	filename = r'c:\Employees.xls'
	file = open(filename)
	main_utils.handle_uploaded_file(file)