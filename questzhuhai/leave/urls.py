from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView
from leave.models import LeaveRequest

from django.contrib.admin.sites import AdminSite
from leave.admin import LeaveRequestAdmin
from leave.models import LeaveRequest
leaverequest_admin = LeaveRequestAdmin(LeaveRequest, AdminSite())

from maitenance.views import admin_require

urlpatterns = patterns('',
	url(r'^leaverequest/new/$', "leave.views.leave_request"),
	url(r'^leaverequest/edit/(?P<id>\d+)/$', "leave.views.leave_request", {'edit': True}, name='leave_request_edit'),
	url(r'^leaverequest/approve/(?P<id>\d+)/$', "leave.views.leave_request_approve", name='leave_request_approve'),
	url(r'^leaverequest/reject/(?P<id>\d+)/$', "leave.views.leave_request_reject", name='leave_request_reject'),
	url(r'^leaverequest/archive/(?P<id>\d+)/$', "leave.views.leave_request_archive", name='leave_request_archive'),
	url(r'^leaverequest/cancel/(?P<id>\d+)/$', "leave.views.leave_request_cancel", name='leave_request_cancel'),
	#url(r'^leaverequests/$', "leave.views.leave_request_by_admin"),
	url(r'^leaverequests/$', admin_require(leaverequest_admin.changelist_view)),
	url(r'^leaverequests/my/$', "leave.views.leave_request_by_emp"),
	url(r'^leaverequests/todo/$', "leave.views.leave_request_by_approver"),
	url(r'^leaverequests/(?P<id>\d+)/$', "leave.views.leave_request_view"),
	url(r'^checkrequest$', "leave.views.check_period"),
)