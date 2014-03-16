/* global $, L, stations: false */
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

  var showStandInfo = function (stand, latlng) {
    var popup = L.popup({
    });
    popup.setLatLng(latlng);
    popup.setContent('test');
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
