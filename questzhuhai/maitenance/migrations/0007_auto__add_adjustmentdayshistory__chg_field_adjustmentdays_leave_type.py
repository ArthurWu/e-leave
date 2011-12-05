# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AdjustmentDaysHistory'
        db.create_table('maitenance_adjustmentdayshistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maitenance.Employee'])),
            ('leave_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['leave.LeaveType'], null=True, blank=True)),
            ('month', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('adjustment_days', self.gf('django.db.models.fields.FloatField')()),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('maitenance', ['AdjustmentDaysHistory'])

        # Changing field 'AdjustmentDays.leave_type'
        db.alter_column('maitenance_adjustmentdays', 'leave_type_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['leave.LeaveType'], null=True))


    def backwards(self, orm):
        
        # Deleting model 'AdjustmentDaysHistory'
        db.delete_table('maitenance_adjustmentdayshistory')

        # Changing field 'AdjustmentDays.leave_type'
        db.alter_column('maitenance_adjustmentdays', 'leave_type_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['leave.LeaveType']))


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
            'leave_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leave.LeaveType']", 'null': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'maitenance.adjustmentdayshistory': {
            'Meta': {'object_name': 'AdjustmentDaysHistory'},
            'adjustment_days': ('django.db.models.fields.FloatField', [], {}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'expire_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leave_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['leave.LeaveType']", 'null': 'True', 'blank': 'True'}),
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
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
        'maitenance.sickleavereport': {
            'Meta': {'object_name': 'SickLeaveReport'},
            'apr_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'aug_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'create_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dec_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Employee']"}),
            'feb_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jan_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jul_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'jun_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'mar_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'may_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'nov_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'oct_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {}),
            'sep_taken': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'sl_entitlement_of': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'taken_in_this_year': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'total_entitled_as_of': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'working_days': ('django.db.models.fields.FloatField', [], {})
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
