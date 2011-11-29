# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MServeProfile'
        db.create_table('dataservice_mserveprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True)),
        ))
        db.send_create_signal('dataservice', ['MServeProfile'])

        # Adding M2M table for field bases on 'MServeProfile'
        db.create_table('dataservice_mserveprofile_bases', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mserveprofile', models.ForeignKey(orm['dataservice.mserveprofile'], null=False)),
            ('namedbase', models.ForeignKey(orm['dataservice.namedbase'], null=False))
        ))
        db.create_unique('dataservice_mserveprofile_bases', ['mserveprofile_id', 'namedbase_id'])

        # Adding M2M table for field auths on 'MServeProfile'
        db.create_table('dataservice_mserveprofile_auths', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('mserveprofile', models.ForeignKey(orm['dataservice.mserveprofile'], null=False)),
            ('auth', models.ForeignKey(orm['dataservice.auth'], null=False))
        ))
        db.create_unique('dataservice_mserveprofile_auths', ['mserveprofile_id', 'auth_id'])

        # Adding model 'ServiceRequest'
        db.create_table('dataservice_servicerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('reason', self.gf('django.db.models.fields.TextField')()),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='servicerequests', null=True, to=orm['dataservice.MServeProfile'])),
            ('state', self.gf('django.db.models.fields.CharField')(default='P', max_length=1)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('dataservice', ['ServiceRequest'])

        # Adding model 'Usage'
        db.create_table('dataservice_usage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.NamedBase'], null=True, blank=True)),
            ('metric', self.gf('django.db.models.fields.CharField')(max_length=4096)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('reports', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('total', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('squares', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('nInProgress', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('rateTime', self.gf('django.db.models.fields.DateTimeField')()),
            ('rate', self.gf('django.db.models.fields.FloatField')()),
            ('rateCumulative', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('dataservice', ['Usage'])

        # Adding model 'NamedBase'
        db.create_table('dataservice_namedbase', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('initial_usage_recorded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('reportnum', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('dataservice', ['NamedBase'])

        # Adding M2M table for field usages on 'NamedBase'
        db.create_table('dataservice_namedbase_usages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('namedbase', models.ForeignKey(orm['dataservice.namedbase'], null=False)),
            ('usage', models.ForeignKey(orm['dataservice.usage'], null=False))
        ))
        db.create_unique('dataservice_namedbase_usages', ['namedbase_id', 'usage_id'])

        # Adding model 'HostingContainer'
        db.create_table('dataservice_hostingcontainer', (
            ('namedbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dataservice.NamedBase'], unique=True, primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('default_profile', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('default_path', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('dataservice', ['HostingContainer'])

        # Adding model 'DataServiceProfile'
        db.create_table('dataservice_dataserviceprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(related_name='profiles', to=orm['dataservice.DataService'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('dataservice', ['DataServiceProfile'])

        # Adding model 'DataServiceWorkflow'
        db.create_table('dataservice_dataserviceworkflow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(related_name='workflows', to=orm['dataservice.DataServiceProfile'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('dataservice', ['DataServiceWorkflow'])

        # Adding model 'DataServiceTaskSet'
        db.create_table('dataservice_dataservicetaskset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('workflow', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasksets', to=orm['dataservice.DataServiceWorkflow'])),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dataservice', ['DataServiceTaskSet'])

        # Adding model 'DataServiceTask'
        db.create_table('dataservice_dataservicetask', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('taskset', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['dataservice.DataServiceTaskSet'])),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('condition', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('args', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('dataservice', ['DataServiceTask'])

        # Adding model 'DataService'
        db.create_table('dataservice_dataservice', (
            ('namedbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dataservice.NamedBase'], unique=True, primary_key=True)),
            ('container', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.HostingContainer'], null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subservices', null=True, to=orm['dataservice.DataService'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('endtime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('dataservice', ['DataService'])

        # Adding model 'RemoteMServeService'
        db.create_table('dataservice_remotemserveservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('dataservice', ['RemoteMServeService'])

        # Adding model 'MFolder'
        db.create_table('dataservice_mfolder', (
            ('namedbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dataservice.NamedBase'], unique=True, primary_key=True)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.DataService'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.MFolder'], null=True)),
            ('duplicate_of', self.gf('django.db.models.fields.related.ForeignKey')(related_name='duplicated_from', null=True, to=orm['dataservice.MFolder'])),
        ))
        db.send_create_signal('dataservice', ['MFolder'])

        # Adding model 'MFile'
        db.create_table('dataservice_mfile', (
            ('namedbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dataservice.NamedBase'], unique=True, primary_key=True)),
            ('empty', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.DataService'])),
            ('folder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.MFolder'], null=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=400, null=True, blank=True)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('checksum', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('size', self.gf('django.db.models.fields.BigIntegerField')(default=0)),
            ('thumb', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('poster', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('proxy', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('duplicate_of', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.MFile'], null=True)),
        ))
        db.send_create_signal('dataservice', ['MFile'])

        # Adding model 'BackupFile'
        db.create_table('dataservice_backupfile', (
            ('namedbase_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dataservice.NamedBase'], unique=True, primary_key=True)),
            ('mfile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.MFile'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=400)),
            ('mimetype', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('checksum', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('dataservice', ['BackupFile'])

        # Adding model 'ManagementProperty'
        db.create_table('dataservice_managementproperty', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.NamedBase'])),
            ('property', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('dataservice', ['ManagementProperty'])

        # Adding model 'Auth'
        db.create_table('dataservice_auth', (
            ('id', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('authname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('base', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.NamedBase'], null=True, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dataservice.Auth'], null=True, blank=True)),
            ('roles_csv', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('dataservice', ['Auth'])

        # Adding M2M table for field usages on 'Auth'
        db.create_table('dataservice_auth_usages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('auth', models.ForeignKey(orm['dataservice.auth'], null=False)),
            ('usage', models.ForeignKey(orm['dataservice.usage'], null=False))
        ))
        db.create_unique('dataservice_auth_usages', ['auth_id', 'usage_id'])


    def backwards(self, orm):
        
        # Deleting model 'MServeProfile'
        db.delete_table('dataservice_mserveprofile')

        # Removing M2M table for field bases on 'MServeProfile'
        db.delete_table('dataservice_mserveprofile_bases')

        # Removing M2M table for field auths on 'MServeProfile'
        db.delete_table('dataservice_mserveprofile_auths')

        # Deleting model 'ServiceRequest'
        db.delete_table('dataservice_servicerequest')

        # Deleting model 'Usage'
        db.delete_table('dataservice_usage')

        # Deleting model 'NamedBase'
        db.delete_table('dataservice_namedbase')

        # Removing M2M table for field usages on 'NamedBase'
        db.delete_table('dataservice_namedbase_usages')

        # Deleting model 'HostingContainer'
        db.delete_table('dataservice_hostingcontainer')

        # Deleting model 'DataServiceProfile'
        db.delete_table('dataservice_dataserviceprofile')

        # Deleting model 'DataServiceWorkflow'
        db.delete_table('dataservice_dataserviceworkflow')

        # Deleting model 'DataServiceTaskSet'
        db.delete_table('dataservice_dataservicetaskset')

        # Deleting model 'DataServiceTask'
        db.delete_table('dataservice_dataservicetask')

        # Deleting model 'DataService'
        db.delete_table('dataservice_dataservice')

        # Deleting model 'RemoteMServeService'
        db.delete_table('dataservice_remotemserveservice')

        # Deleting model 'MFolder'
        db.delete_table('dataservice_mfolder')

        # Deleting model 'MFile'
        db.delete_table('dataservice_mfile')

        # Deleting model 'BackupFile'
        db.delete_table('dataservice_backupfile')

        # Deleting model 'ManagementProperty'
        db.delete_table('dataservice_managementproperty')

        # Deleting model 'Auth'
        db.delete_table('dataservice_auth')

        # Removing M2M table for field usages on 'Auth'
        db.delete_table('dataservice_auth_usages')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dataservice.auth': {
            'Meta': {'object_name': 'Auth'},
            'authname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.Auth']", 'null': 'True', 'blank': 'True'}),
            'roles_csv': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dataservice.Usage']", 'symmetrical': 'False'})
        },
        'dataservice.backupfile': {
            'Meta': {'object_name': 'BackupFile', '_ormbases': ['dataservice.NamedBase']},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400'}),
            'mfile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFile']"}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dataservice.dataservice': {
            'Meta': {'object_name': 'DataService', '_ormbases': ['dataservice.NamedBase']},
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.HostingContainer']", 'null': 'True', 'blank': 'True'}),
            'endtime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subservices'", 'null': 'True', 'to': "orm['dataservice.DataService']"}),
            'priority': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dataservice.dataserviceprofile': {
            'Meta': {'object_name': 'DataServiceProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'profiles'", 'to': "orm['dataservice.DataService']"})
        },
        'dataservice.dataservicetask': {
            'Meta': {'object_name': 'DataServiceTask'},
            'args': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'condition': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'taskset': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['dataservice.DataServiceTaskSet']"})
        },
        'dataservice.dataservicetaskset': {
            'Meta': {'ordering': "['order']", 'object_name': 'DataServiceTaskSet'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'workflow': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasksets'", 'to': "orm['dataservice.DataServiceWorkflow']"})
        },
        'dataservice.dataserviceworkflow': {
            'Meta': {'object_name': 'DataServiceWorkflow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'workflows'", 'to': "orm['dataservice.DataServiceProfile']"})
        },
        'dataservice.hostingcontainer': {
            'Meta': {'object_name': 'HostingContainer', '_ormbases': ['dataservice.NamedBase']},
            'default_path': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'default_profile': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dataservice.managementproperty': {
            'Meta': {'object_name': 'ManagementProperty'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'dataservice.mfile': {
            'Meta': {'ordering': "('-created', 'name')", 'object_name': 'MFile', '_ormbases': ['dataservice.NamedBase']},
            'checksum': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFile']", 'null': 'True'}),
            'empty': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '400', 'null': 'True', 'blank': 'True'}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFolder']", 'null': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'poster': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'proxy': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.DataService']"}),
            'size': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'thumb': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dataservice.mfolder': {
            'Meta': {'object_name': 'MFolder', '_ormbases': ['dataservice.NamedBase']},
            'duplicate_of': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'duplicated_from'", 'null': 'True', 'to': "orm['dataservice.MFolder']"}),
            'namedbase_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dataservice.NamedBase']", 'unique': 'True', 'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.MFolder']", 'null': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.DataService']"})
        },
        'dataservice.mserveprofile': {
            'Meta': {'object_name': 'MServeProfile'},
            'auths': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'profileauths'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dataservice.Auth']"}),
            'bases': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'bases'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dataservice.NamedBase']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'dataservice.namedbase': {
            'Meta': {'object_name': 'NamedBase'},
            'id': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'initial_usage_recorded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reportnum': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'usages': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dataservice.Usage']", 'symmetrical': 'False'})
        },
        'dataservice.remotemserveservice': {
            'Meta': {'object_name': 'RemoteMServeService'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'dataservice.servicerequest': {
            'Meta': {'ordering': "['-time']", 'object_name': 'ServiceRequest'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'servicerequests'", 'null': 'True', 'to': "orm['dataservice.MServeProfile']"}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'P'", 'max_length': '1'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'dataservice.usage': {
            'Meta': {'object_name': 'Usage'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dataservice.NamedBase']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metric': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'nInProgress': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'rate': ('django.db.models.fields.FloatField', [], {}),
            'rateCumulative': ('django.db.models.fields.FloatField', [], {}),
            'rateTime': ('django.db.models.fields.DateTimeField', [], {}),
            'reports': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'squares': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['dataservice']
