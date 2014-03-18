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
            # 'street': station.street,
            # 'zip': station.zip,
            'status': station.latest_snapshot.status,
            'bikes': station.latest_snapshot.bikes,
            'docks': station.latest_snapshot.docks,
            'url': station.resource_url,
        }

    def get_context_data(self, **kwargs):
        data = super(MarketDetail, self).get_context_data(**kwargs)
        serializer = DjangoJSONEncoder()
        stations = (self.object.stations.all()
            .order_by('-latest_snapshot__timestamp')
            .select_related('latest_snapshot')
        )
        data['stations'] = stations
        json_data = {
            'stations': map(self.station_to_json, stations),
            'updated_at': stations[0].updated_at,
        }
        data['station_json'] = serializer.encode(json_data)
        return data


class MarketResource(MarketDetail):
    def get(self, request, **kwargs):
        self.object = self.get_object()
        data = self.get_context_data(**kwargs)
        return HttpResponse(data['station_json'], content_type='application/json')


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
        del_window = datetime.timedelta(hours=12)
        serializer = DjangoJSONEncoder()
        station = self.model.objects.get(market__slug=kwargs['slug'],
                slug=kwargs['station_slug'])

        # make querysets
        recent_start = timezone.now() - datetime.timedelta(hours=11)
        recent_qs = station.history.filter(
            timestamp__gt=recent_start,
            timestamp__lte=recent_start + del_window,
        )
        yesterday_start = recent_start - datetime.timedelta(days=1)
        yesterday_qs = station.history.filter(
            timestamp__gt=yesterday_start,
            timestamp__lte=yesterday_start + del_window,
        )
        lastweek_start = recent_start - datetime.timedelta(days=7)
        lastweek_qs = station.history.filter(
            timestamp__gt=lastweek_start,
            timestamp__lte=lastweek_start + del_window,
        )

        # convert querysets to json
        recent = map(self.snapshot_to_json, recent_qs)
        yesterday = map(self.snapshot_to_json, yesterday_qs)
        lastweek = map(self.snapshot_to_json, lastweek_qs)

        data = {
            'capacity': station.capacity,
            'recent': recent,
            'yesterday': yesterday,
            'lastweek': lastweek,
        }
        return HttpResponse(serializer.encode(data),
                content_type='application/json')
