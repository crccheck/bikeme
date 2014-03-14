from django.contrib import admin

from . import models


admin.site.register(models.Market)

admin.site.register(models.Station)


class StationSnapshotAdmin(admin.ModelAdmin):
    date_heirarch = 'timestamp'
    list_display = ('station', 'bikes', 'docks', 'timestamp')
    list_filter = ('station', )

admin.site.register(models.StationSnapshot, StationSnapshotAdmin)
