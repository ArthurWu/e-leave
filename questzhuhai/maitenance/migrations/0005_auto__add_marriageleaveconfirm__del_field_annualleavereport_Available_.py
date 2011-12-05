# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MarriageLeaveConfirm'
        db.create_table('maitenance_marriageleaveconfirm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maitenance.Employee'])),
            ('days', self.gf('django.db.models.fields.FloatField')()),
            ('marrige_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('expire_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('maitenance', ['MarriageLeaveConfirm'])

        # Deleting field 'AnnualLeaveReport.Available_annual_leave_unclaimed'
        db.delete_column('maitenance_annualleavereport', 'Available_annual_leave_unclaimed')

        # Deleting field 'AnnualLeaveReport.Application_comp_leave'
        db.delete_column('maitenance_annualleavereport', 'Application_comp_leave')

        # Deleting field 'AnnualLeaveReport.Taken_in_this_year'
        db.delete_column('maitenance_annualleavereport', 'Taken_in_this_year')

        # Adding field 'AnnualLeaveReport.taken_in_this_year'
        db.add_column('maitenance_annualleavereport', 'taken_in_this_year', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Adding field 'AnnualLeaveReport.available_annual_leave_unclaimed'
        db.add_column('maitenance_annualleavereport', 'available_annual_leave_unclaimed', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Adding field 'AnnualLeaveReport.application_comp_leave'
        db.add_column('maitenance_annualleavereport', 'application_comp_leave', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'MarriageLeaveConfirm'
        db.delete_table('maitenance_marriageleaveconfirm')

        # Adding field 'AnnualLeaveReport.Available_annual_leave_unclaimed'
        db.add_column('maitenance_annualleavereport', 'Available_annual_leave_unclaimed', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Adding field 'AnnualLeaveReport.Application_comp_leave'
        db.add_column('maitenance_annualleavereport', 'Application_comp_leave', self.gf('django.db.models.fields.FloatField')(null=True), keep_default=False)

        # Adding field 'AnnualLeaveReport.Taken_in_this_year'
        db.add_column('maitenance_annualleavereport', 'Taken_in_this_year', self.gf('django.db.models.fields.FloatField')(default=0.0), keep_default=False)

        # Deleting field 'AnnualLeaveReport.taken_in_this_year'
        db.delete_column('maitenance_annualleavereport', 'taken_in_this_year')

        # Deleting field 'AnnualLeaveReport.available_annual_leave_unclaimed'
        db.delete_column('maitenance_annualleavereport', 'available_annual_leave_unclaimed')

        # Deleting field 'AnnualLeaveReport.application_comp_leave'
        db.delete_column('maitenance_annualleavereport', 'application_comp_leave')


    models = {
        'leave.leavetype': {
            'Meta': {'object_name': 'LeaveType'},
            'build_in': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_days': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'unique': 'True'}),
            'notifyadmin': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'maitenance.adjustmentdays': {
            'Meta': {'object_name': 'AdjustmentDays'},
            'adjustment_days': ('django.db.models.fields.FloatField', [], {}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leave_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leave.LeaveType']"}),
            'month': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'maitenance.admin': {
            'Meta': {'object_name': 'Admin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'})
        },
        'maitenance.annualleavereport': {
            'Meta': {'object_name': 'AnnualLeaveReport'},
            'al_entitlement_of': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'application_comp_leave': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'apr_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'apr_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'aug_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'aug_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'available_annual_leave_unclaimed': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'balance_of_comp_leave': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'dec_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'dec_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'feb_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'feb_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jan_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jan_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jul_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jul_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jun_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jun_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mar_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mar_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'marrige_leave_balance': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'may_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'may_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'nov_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'nov_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'oct_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'oct_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {}),
            'sep_deduction': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'sep_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'taken_comp_leave': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'taken_in_this_year': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'total_entitled_as_of': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'working_days': ('django.db.models.fields.FloatField', [], {})
        },
        'maitenance.department': {
            'Meta': {'object_name': 'Department'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'}),
            'supervisor': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        'maitenance.employee': {
            'Meta': {'object_name': 'Employee'},
            'al_entitlement': ('django.db.models.fields.FloatField', [], {}),
            'approvers': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'balanced_days': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'balanced_forward': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cc_to': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'chinese_name': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'department': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employees'", 'blank': 'True', 'null': 'True', 'to': "orm['maitenance.Department']"}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'domain_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_administrative_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'join_date': ('django.db.models.fields.DateField', [], {}),
            'last_login_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'sid': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'}),
            'sl_entitlement': ('django.db.models.fields.FloatField', [], {}),
            'start_fiscal_date': ('django.db.models.fields.DateField', [], {}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'team_members'", 'blank': 'True', 'null': 'True', 'to': "orm['maitenance.Team']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'maitenance.maintenancelog': {
            'Meta': {'object_name': 'MaintenanceLog'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'when': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'who': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'maitenance.marriageleaveconfirm': {
            'Meta': {'object_name': 'MarriageLeaveConfirm'},
            'days': ('django.db.models.fields.FloatField', [], {}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'expire_date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marrige_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'maitenance.team': {
            'Meta': {'object_name': 'Team'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'})
        }
    }

    complete_apps = ['maitenance']
