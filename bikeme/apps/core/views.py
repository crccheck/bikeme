import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import ListView, DetailView

from . import models


class Landing(ListView):
    model = models.Market


class MarketDetail(DetailView):
    model = models.Market

    @staticmethod
    def station_to_json(station):
        return {
            'name': station.name,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'street': station.street,
            'zip': station.zip,
            'status': station.latest_snapshot.status,
            'bikes': station.latest_snapshot.bikes,
            'docks': station.latest_snapshot.docks,
            'url': station.resource_url,
        }

    def get_context_data(self, **kwargs):
        data = super(MarketDetail, self).get_context_data(**kwargs)
        serializer = DjangoJSONEncoder()
        stations = self.object.stations.all().select_related('latest_snapshot')
        data['station_json'] = serializer.encode(map(self.station_to_json, stations))
        return data


class StationResource(DetailView):
    model = models.Station

    @staticmethod
    def snapshot_to_json(obj):
        # try to save a few bytes by using an array instead of an object
        return [
            obj.timestamp,
            obj.status,
            obj.bikes,
            obj.docks,
        ]

    def get(self, request, **kwargs):
        del_recent = datetime.timedelta(hours=12)
        del_day = datetime.timedelta(days=1)
        del_week = datetime.timedelta(days=7)
        serializer = DjangoJSONEncoder()
        station = self.model.objects.get(market__slug=kwargs['slug'],
                slug=kwargs['station_slug'])

        # make querysets
        recent_qs = station.history.filter(
                timestamp__gt=timezone.now() - del_recent)
        yesterday_qs = station.history.filter(
            timestamp__lte=timezone.now() - del_day,
            timestamp__gt=timezone.now() - del_recent - del_day,
        )
        lastweek_qs = station.history.filter(
            timestamp__lte=timezone.now() - del_week,
            timestamp__gt=timezone.now() - del_recent - del_week,
        )

        # convert querysets to json
        recent = map(self.snapshot_to_json, recent_qs)
        yesterday = map(self.snapshot_to_json, yesterday_qs)
        lastweek = map(self.snapshot_to_json, lastweek_qs)

        data = {
            'recent': recent,
            'yesterday': yesterday,
            'lastweek': lastweek,
        }
        return HttpResponse(serializer.encode(data),
                content_type='application/json')
