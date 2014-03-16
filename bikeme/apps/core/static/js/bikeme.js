/* global $, L, d3, stations: false */
(function () {
  'use strict';

  var getIcon = function (stand) {
    // http://leafletjs.com/reference.html#divicon
    var filled = Math.round(stand.bikes / (stand.bikes + stand.docks) * 10);
    return L.divIcon({
      className: 'filled-marker',
      html: '<div class="filled-' + filled + '">X</div>',
      iconAnchornSize: null,
      iconAnchor: null
    });
  };

  var buildChart = function ($el, data) {
    var plotBox = {
      width: 700,
      height: 100
    };

    var format = d3.time.format('%Y-%m-%dT%H:%M:%SZ');

    var cleanedData = data.recent.map(function (d) {
      return {
        date: format.parse(d[0]),
        bikes: d[2],
        docks: d[3]
      };
    });

    var access = {
      x: function (d) { return d.date; },
      bikes: function (d) { return d[2]; },
      docks: function (d) { return d[3]; }
    };


    var svg = d3.select($el[0])
      .append('svg')
      .attr('width', '350')
      .attr('height', '50')
      .attr('viewBox', '0 0 700 100')
      .attr('preserveAspectRatio', 'xMinYMin meet');

    var plot = svg
      .append('g')
      .attr('class', 'plot')
      .attr('width', '700')
      .attr('height', '100')
      .attr('transform', 'translate(0, 0)');

    var xScale = d3.time.scale()
      .range([0, plotBox.width])
      .domain(d3.extent(cleanedData, access.x));

    var yScale = d3.scale.linear()
      .range([0, plotBox.height])
      .domain([0, 20]);

    var line = d3.svg.line()
      .x(function (d) { return xScale(d.date); })
      .y(function (d) { return yScale(d.bikes); });

    plot.append('path')
      .datum(cleanedData)
      .attr('class', 'line')
      .attr('d', line);
  };

  var showStandInfo = function (stand, latlng) {
    var popup = L.popup({
    });
    $.getJSON(stand.url, function (data) {
      var $paper = $('<div>data</div>');
      buildChart($paper, data);
      popup.setContent($paper[0]);
    });
    popup.setLatLng(latlng);
    popup.setContent('loading...');
    popup.openOn(map);
  };

  // create a map in the "map" div, set the view to a given place and zoom
  var map = L.map('map', {
        // scrollWheelZoom: false
      }),
      bounds = [];

  $.each(stations, function (idx, stand) {
    bounds.push([stand.latitude, stand.longitude]);
    var marker = L.marker([stand.latitude, stand.longitude], {
      icon: getIcon(stand),
      title: stand.name + '\nBikes: ' + stand.bikes + '\nDocks: ' + stand.docks
    }).addTo(map);
    marker.on('click', function (e) {
      showStandInfo(stand, e.latlng);
    });
  });

  // add an OpenStreetMap tile layer
  L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', {
    attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">'
  }).addTo(map);

  map.fitBounds(bounds);


  // ***************
  // * GEOLOCATION *
  // ***************

  var myLocation = null;

  var zoomMap = function (position) {
    myLocation = L.latLng(position.coords.latitude, position.coords.longitude);
    map.panTo(myLocation);
    map.setZoom(16);
    L.marker(myLocation).addTo(map);
    map.addControl(new GoHomeControl());
  };

  var GoHomeControl = L.Control.extend({
    options: {
      position: 'topright'
    },
    onAdd: function (map) {
      var container = L.DomUtil.create('div', 'leaflet-control-home leaflet-bar');
      $(container).html('<a class="" href="#" title="Go home"><span class="fa fa-crosshairs"></span></a>')
        .find('a').on('click', function (e) {
          e.preventDefault();
          map.panTo(myLocation);
        });
      return container;
    }
  });

  navigator.geolocation.getCurrentPosition(zoomMap);

})();
