# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Admin'
        db.create_table('maitenance_admin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('maitenance', ['Admin'])

        # Adding model 'MaintenanceLog'
        db.create_table('maitenance_maintenancelog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('when', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('who', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('operation', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('maitenance', ['MaintenanceLog'])

        # Adding model 'Department'
        db.create_table('maitenance_department', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True)),
            ('supervisor', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
        ))
        db.send_create_signal('maitenance', ['Department'])

        # Adding model 'Team'
        db.create_table('maitenance_team', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maitenance.Department'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True)),
            ('leader', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
        ))
        db.send_create_signal('maitenance', ['Team'])

        # Adding model 'Employee'
        db.create_table('maitenance_employee', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(max_length=512, unique=True)),
            ('domain_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('chinese_name', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('department', self.gf('django.db.models.fields.related.ForeignKey')(related_name='employees', blank=True, null=True, to=orm['maitenance.Department'])),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(related_name='team_members', blank=True, null=True, to=orm['maitenance.Team'])),
            ('join_date', self.gf('django.db.models.fields.DateField')()),
            ('start_fiscal_date', self.gf('django.db.models.fields.DateField')()),
            ('balanced_forward', self.gf('django.db.models.fields.FloatField')()),
            ('al_entitlement', self.gf('django.db.models.fields.FloatField')()),
            ('sl_entitlement', self.gf('django.db.models.fields.FloatField')()),
            ('approvers', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('cc_to', self.gf('django.db.models.fields.CharField')(max_length=512, null=True, blank=True)),
            ('is_administrative_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('last_login_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('balanced_days', self.gf('django.db.models.fields.FloatField')(default=0)),
        ))
        db.send_create_signal('maitenance', ['Employee'])

        # Adding model 'AdjustmentDays'
        db.create_table('maitenance_adjustmentdays', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['maitenance.Employee'])),
            ('leave_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['leave.LeaveType'])),
            ('month', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('adjustment_days', self.gf('django.db.models.fields.FloatField')()),
            ('expire_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('maitenance', ['AdjustmentDays'])


    def backwards(self, orm):
        
        # Deleting model 'Admin'
        db.delete_table('maitenance_admin')

        # Deleting model 'MaintenanceLog'
        db.delete_table('maitenance_maintenancelog')

        # Deleting model 'Department'
        db.delete_table('maitenance_department')

        # Deleting model 'Team'
        db.delete_table('maitenance_team')

        # Deleting model 'Employee'
        db.delete_table('maitenance_employee')

        # Deleting model 'AdjustmentDays'
        db.delete_table('maitenance_adjustmentdays')


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
            'balanced_forward': ('django.db.models.fields.FloatField', [], {}),
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
        'maitenance.team': {
            'Meta': {'object_name': 'Team'},
            'department': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['maitenance.Department']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'leader': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512', 'unique': 'True'})
        }
    }

    complete_apps = ['maitenance']
