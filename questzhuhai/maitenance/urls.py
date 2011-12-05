from django.conf.urls.defaults import patterns, include, url
from maitenance.admin import *
from maitenance.models import *
from django.contrib.admin.sites import AdminSite
from views import admin_require

employee_admin = EmployeeAdmin(Employee, AdminSite())
dep_admin = DepartmentAdmin(Department, AdminSite())
team_admin = TeamAdmin(Team, AdminSite())

urlpatterns = patterns('',
    url(r'^reports/$', "maitenance.views.reports"),
    url(r'^settings/$', "maitenance.views.maitenance"),
    url(r'^admin/add$', "maitenance.views.add_admin"),
    url(r'^admin/delete$', "maitenance.views.delete_admin"),
    url(r'^leavetype/add$', "maitenance.views.add_leave_type"),
    url(r'^leavetype/delete$', "maitenance.views.delete_leave_type"),
    url(r'^leavetype/set_notify_admin$', "maitenance.views.set_notify_admin"),
    url(r'^deps_teams$', "maitenance.views.add_department_view"),
    url(r'^dep/add$', "maitenance.views.add_department_view"),
    url(r'^dep/delete$', "maitenance.views.delete_department"),
    url(r'^get_teams_by_department$', "maitenance.views.get_teams_by_department"),
    url(r'^team/add$', "maitenance.views.add_team"),
    url(r'^team/delete$', "maitenance.views.delete_team"),
    url(r'^employees/$', admin_require(employee_admin.changelist_view)),
    url(r'^employees/add/$', admin_require(employee_admin.add_view)),
    url(r'^employees/(?P<object_id>\d+)/$', admin_require(employee_admin.change_view)),
    url(r'^employees/(?P<object_id>\d+)/delete/$', admin_require(employee_admin.delete_view)),

	url(r'^department/$', admin_require(dep_admin.changelist_view)),
	url(r'^department/add/$', admin_require(dep_admin.add_view)),
	url(r'^department/(?P<object_id>\d+)/$', admin_require(dep_admin.change_view)),
	url(r'^department/(?P<object_id>\d+)/delete/$', admin_require(dep_admin.delete_view)),
	
	url(r'^team/$', admin_require(team_admin.changelist_view)),
	url(r'^team/add/$', admin_require(team_admin.add_view)),
	url(r'^team/(?P<object_id>\d+)/$', admin_require(team_admin.change_view)),
	url(r'^team/(?P<object_id>\d+)/delete/$', admin_require(team_admin.delete_view)),
	
	url(r'^import_employees/$', 'maitenance.views.import_employees'),
	url(r'^action_logs/$', 'maitenance.views.action_logs'),
	
	url(r'^(\w+)/add$', 'maitenance.views.add_object'),
	#url(r'^(\w+)/delete$', 'maitenance.views.delete_object'),
	
	url(r'^reports/$', 'maitenance.views.reports'),
	url(r'^reports/generate$', 'maitenance.views.generate_report'),
	url(r'^reports/download/(?P<report_type>\w+)/(?P<start_date>\w{10})/(?P<end_date>\w{10})/$',
		'maitenance.views.download_leave_record_report', name='download_leave_record_report'),
	url(r'^reports/download/(?P<report_type>\w+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
		'maitenance.views.download_report', name='download_report'),
)