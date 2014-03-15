# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Station.latest_snapshot'
        db.add_column(u'core_station', 'latest_snapshot',
                      self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='+', unique=True, null=True, to=orm['core.Snapshot']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Station.latest_snapshot'
        db.delete_column(u'core_station', 'latest_snapshot_id')


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
            'latest_snapshot': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'+'", 'unique': 'True', 'null': 'True', 'to': u"orm['core.Snapshot']"}),
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