from django.views.generic import ListView, DetailView
from django.core.serializers.json import DjangoJSONEncoder

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
        }

    def get_context_data(self, **kwargs):
        data = super(MarketDetail, self).get_context_data(**kwargs)
        serializer = DjangoJSONEncoder()
        stations = self.object.stations.all()
        data['station_json'] = serializer.encode(map(self.station_to_json, stations))
        return data
