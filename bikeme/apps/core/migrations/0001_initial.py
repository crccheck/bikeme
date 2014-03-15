# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Market'
        db.create_table(u'core_market', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=30)),
        ))
        db.send_create_signal(u'core', ['Market'])

        # Adding model 'Station'
        db.create_table(u'core_station', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60)),
            ('market', self.gf('django.db.models.fields.related.ForeignKey')(related_name='stations', to=orm['core.Market'])),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=5)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=5)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=120)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('capacity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'core', ['Station'])

        # Adding unique constraint on 'Station', fields ['slug', 'market']
        db.create_unique(u'core_station', ['slug', 'market_id'])

        # Adding model 'Snapshot'
        db.create_table(u'core_snapshot', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('station', self.gf('django.db.models.fields.related.ForeignKey')(related_name='history', to=orm['core.Station'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('bikes', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('docks', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'core', ['Snapshot'])


    def backwards(self, orm):
        # Removing unique constraint on 'Station', fields ['slug', 'market']
        db.delete_unique(u'core_station', ['slug', 'market_id'])

        # Deleting model 'Market'
        db.delete_table(u'core_market')

        # Deleting model 'Station'
        db.delete_table(u'core_station')

        # Deleting model 'Snapshot'
        db.delete_table(u'core_snapshot')


    models = {
        u'core.market': {
            'Meta': {'object_name': 'Market'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'core.snapshot': {
            'Meta': {'ordering': "('timestamp',)", 'object_name': 'Snapshot'},
            'bikes': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'docks': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'station': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'history'", 'to': u"orm['core.Station']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'core.station': {
            'Meta': {'ordering': "('market', 'name')", 'unique_together': "(('slug', 'market'),)", 'object_name': 'Station'},
            'capacity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '5'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '5'}),
            'market': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stations'", 'to': u"orm['core.Market']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        }
    }

    complete_apps = ['core']