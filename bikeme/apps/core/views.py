from django.views.generic import ListView, DetailView

from . import models


class Landing(ListView):
    model = models.Market


class MarketDetail(DetailView):
    model = models.Market
