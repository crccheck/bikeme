/* global $, L, d3, _: false */
/* global station_data: true */
(function () {
  'use strict';

  // Lets us turn json dates into javascript dates
  var isoToDate = d3.time.format('%Y-%m-%dT%H:%M:%SZ');
  var tzOffset = new Date().getTimezoneOffset() / -60;
  var updated_at = d3.time.hour.offset(isoToDate.parse(station_data.updated_at), tzOffset);


  //*******************
  //* D3 AWWWW YISSSS *
  //*******************

  var buildChart = function ($el, data) {
    var plotBox = {
      width: Math.max(300, $(window).width() >> 1),
      height: 200
    };
    var plotMargin = {
      top: 8,
      left: 24,
      bottom: 42,
      right: 7
    };

    var cleaner = function (days) {
      return function (d) {
        return {
          date: d3.time.day.offset(
            d3.time.hour.offset(isoToDate.parse(d[0]), tzOffset),
            days
          ),
          bikes: d[2],
          docks: d[3]
        };
      };
    };
    var cleanedData = {
      recent: data.recent.map(cleaner(0)),
      yesterday: data.yesterday.map(cleaner(1)),
      lastweek: data.lastweek.map(cleaner(7))
    };

    $el.find('.loading').remove();
    // update status since `updateMaps` can't access the popup content
    var latestData = data.recent[data.recent.length - 1];
    $el.find('.status-bikes').html(latestData[2]);
    $el.find('.status-docks').html(latestData[3]);
    $el.find('.status-status').html(latestData[1]);

    var svg = d3.select($el[0])
      .append('svg')
      .attr('width', plotBox.width + plotMargin.left + plotMargin.right)
      .attr('height', plotBox.height + plotMargin.top + plotMargin.bottom)
      .attr('viewBox', [0, 0,
          plotBox.width + plotMargin.left + plotMargin.right,
          plotBox.height + plotMargin.top + plotMargin.bottom,
        ].join(' '))
      .attr('preserveAspectRatio', 'xMinYMin meet');

    var plot = svg
      .append('g')
      .attr('class', 'plot')
      .attr('width', plotBox.width)
      .attr('height', plotBox.height)
      .attr('transform', 'translate(' + plotMargin.left + ', ' + plotMargin.top + ')');

    var minValues = [cleanedData.recent[0].date],
        maxValues = [cleanedData.recent[cleanedData.recent.length - 1].date];
    if (cleanedData.yesterday.length) {
      minValues.push(cleanedData.yesterday[0].date);
      maxValues.push(cleanedData.yesterday[cleanedData.yesterday.length - 1].date);
    }
    var xScale = d3.time.scale()
      .range([0, plotBox.width])
      .domain([
        Math.min.apply(undefined, minValues),
        Math.max.apply(undefined, maxValues)
      ]);

    var yScale = d3.scale.linear()
      .range([0, plotBox.height])
      .domain([data.capacity, 0]);

    var xAxis = d3.svg.axis()
      .scale(xScale)
      .orient('bottom');

    var yAxis = d3.svg.axis()
      .scale(yScale)
      .orient('left');
    if (data.capacity < 10) {
      // Because you can't have 3.5 bikes
      yAxis.ticks(data.capacity);
    }

    var line = d3.svg.line()
      .x(function (d) { return xScale(d.date); })
      .y(function (d) { return yScale(d.bikes); });
    var area = d3.svg.area()
      .x(function (d) { return xScale(d.date); })
      .y0(plotBox.height)
      .y1(function (d) { return yScale(d.bikes); });

    svg.append('g')
      .attr('class', 'x axis')
      .attr('transform', 'translate(' + plotMargin.left + ', ' + (plotBox.height + plotMargin.top) + ')')
      .call(xAxis)
      .selectAll('text')
        .style('text-anchor', 'end')
        .attr('dx', '-0.8em')
        .attr('dy', '0.15em')
        .attr('transform', 'rotate(-35)');

    svg.append('g')
      .attr('class', 'y axis')
      .attr('transform', 'translate(' + plotMargin.left + ', ' + plotMargin.top + ')')
      .call(yAxis);

    $.each(['yesterday', 'recent'], function (idx, dataset) {
      plot.append('path')
        .datum(cleanedData[dataset])
        .attr('class', 'area ' + dataset)
        .attr('d', area);
      plot.append('path')
        .datum(cleanedData[dataset])
        .attr('class', 'line ' + dataset)
        .attr('d', line);
    });

    plot.append('line')
      .attr('class', 'now')
      .attr('x1', 0)
      .attr('y1', 0)
      .attr('x2', 0)
      .attr('y2', plotBox.height)
      .attr('stroke-dasharray', '5, 5')
      .attr('transform', 'translate(' + xScale(new Date()) + ', 0)');
  };


  // *************
  // * MAP POPUP *
  // *************

  var getPopupContent = function (station) {
    var $paper = $('<div><h3>' + station.name + '</h3>' +
      '<div>Bikes: <i class="status-bikes">' + station.bikes + '</i>' +
      ' Docks: <i class="status-docks">' + station.docks + '</i>' +
      ' Status: <i class="status-status">' + station.status + '</i>' +
      ' Legend: <span class="indicator recent">Now</span>' +
      ' <span class="indicator yesterday">Yesterday</span>' +
      '</div>' +
      '<div class="loading">Loading... <i class="fa fa-spinner fa-spin"></i></div>' +
      '</div>');
    return $paper;
  };


  // **************
  // * CREATE MAP *
  // **************

  var getIcon = function (station) {
    // http://leafletjs.com/reference.html#divicon
    var filled = Math.round(station.bikes / (station.bikes + station.docks) * 10);
    if (filled === 0 && station.bikes) {
      filled = 1;
    } else if (filled === 10 && station.docks) {
      filled = 9;
    }
    return L.divIcon({
      className: 'filled-marker',
      html: '<div class="marker-inner ' + station.status + '">' +
        '<span class="filled-' + filled + '">X</span></div>',
      iconSize: [24, 24],
      iconAnchor: null
    });
  };


  var map = L.map('map', {
        // scrollWheelZoom: false
      }),
      markers = {},
      bounds = [];

  var createMap = function () {
    $.each(station_data.stations, function (idx, station) {
      var slug = station.url.match(/([\w\-]+).json/)[1];
      bounds.push([station.latitude, station.longitude]);
      var marker = L.marker([station.latitude, station.longitude], {
        icon: getIcon(station),
        title: station.name + '\nBikes: ' + station.bikes + '\nDocks: ' + station.docks
      }).addTo(map);
      marker.bindPopup(L.popup({
        // keep popup from cutting off chart
        maxWidth: 10000
      }));
      marker.on('click', function () {
        // HACK because marker.on('popupopen') does not work
        var popup = marker.getPopup();
        if (!popup._isOpen) {
          // bail
          return;
        }
        var $paper = getPopupContent(station);
        popup.setContent($paper[0]);
        $.getJSON(station.url, function (data) {
          buildChart($paper, data);
          popup.update();  // update popup dimensions
        });
        state.push(slug);
      });
      markers[slug] = marker;
    });

    // add an OpenStreetMap tile layer
    L.tileLayer('http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png', {
      attribution: 'Tiles Courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png">'
    }).addTo(map);

    map.fitBounds(bounds);
  };
  var lastUpdate = Date.now();
  var updateMap = function () {
    var url = location.pathname + 'data.json';
    return $.getJSON(url, function (data) {
      station_data = data;  // update local storage
      updated_at = d3.time.hour.offset(isoToDate.parse(station_data.updated_at), tzOffset);
      lastUpdate = Date.now() + 15 * 1000;  // lie and set `lastUpdate` to the future
      $.each(station_data.stations, function (idx, stand) {
        var slug = stand.url.match(/([\w\-]+).json/)[1];
        var marker = markers[slug];
        marker.setIcon(getIcon(stand));
      });
    });
  };


  // ***************
  // * AUTO UPDATE *
  // ***************

  var autoUpdateControl = L.control({position: 'bottomleft'}),
      $autoUpdateControl = $('<div class="autoupdate">Last Update: <span class="last"></span>s' +
        ' Next Update: <span class="next"></span>s</div>');
  autoUpdateControl.onAdd = function () {
    var $last = $autoUpdateControl.find('.last'),
        $next = $autoUpdateControl.find('.next');
    var next = 10 * 60;  // 10 minutes
    var _update = function () {
      var diff = (Date.now() - updated_at) / 1000,
          nextDiff = next - diff;
      $last.html(Math.floor(diff));
      if (nextDiff < 0) {
        var msg = lastUpdate ? 'in progres' : 'oop';
        $next.html('<span style="font-weight: normal;">' + msg + '</span>');
      } else {
        $next.html(Math.floor(nextDiff));
      }
      var now = Date.now();
      // wait at least 5 seconds between updates
      if (nextDiff < 0 && lastUpdate && (now - lastUpdate) > 5000) {
        updateMap()
          .fail(function () {
            lastUpdate = false;
          });
        lastUpdate = now;
      }
    };
    _update();
    setInterval(_update, 1000);
    return $autoUpdateControl[0];
  };


  // ***************
  // * GEOLOCATION *
  // ***************

  var topRight = {
    $el: $('<div class="leaflet-control-home leaflet-bar"></div>'),
    myLocation: null,
    myLocationMarker: null,
    addMyLocationBtn: function (){
      var $btn = $('<a class="action-home" href="#" title="Go home"><span class="fa fa-location-arrow"></span></a>')
        .on('click', function (e) {
          e.preventDefault();
          navigator.geolocation.getCurrentPosition(topRight.panToPosition);
        });
      this.$el.append($btn);
    },
    initialPositionFound: function (position) {
      var self = topRight;
      self.myLocation = L.latLng(position.coords.latitude, position.coords.longitude);
      self.myLocationMarker = L.marker(self.myLocation).addTo(map);
      self.addMyLocationBtn();
      if (map.getBounds().contains(self.myLocation)) {
        // only pan if user's location is worth panning to
        map.panTo(self.myLocation);
        map.setZoom(16);
      }
    },
    panToPosition: function (position) {
      var self = topRight;
      self.myLocation = L.latLng(position.coords.latitude, position.coords.longitude);
      self.myLocationMarker.setLatLng(self.myLocation);
      map.panTo(self.myLocation);
    },
    init: function () {
      var goHomeControl = L.control({position: 'topright'});
      goHomeControl.onAdd = function (map) {
        var $btn = $('<a class="action-all" href="#" title="View system map"><span class="fa fa-arrows-alt"></span></a>')
          .on('click', function (e) {
            e.preventDefault();
            map.fitBounds(bounds);
          });
          topRight.$el.append($btn);
        return topRight.$el[0];
      };
      goHomeControl.addTo(map);

      navigator.geolocation.getCurrentPosition(topRight.initialPositionFound);
    }
  };


  // *****************
  // * LOCATION HASH *
  // *****************
  var state = {
    _state: document.location.hash.substr(1),
    push: _.debounce(function (newState) {
      state._state = newState;
      if (newState === '') {
        // remove hash, including the `#`
        history.replaceState('', document.title, window.location.pathname);
      } else {
        document.location.hash = newState;
      }
    }, 200)
  };
  var initLocationHash = function () {
    var slug = document.location.hash.substr(1);
    if (slug && markers[slug]) {
      markers[slug].fireEvent('click');
    }
    map.on('popupclose', function () {
      state.push('');
    });
    $(window).on('hashchange', function () {
      var slug = document.location.hash.substr(1);
      if (slug === '') {
        map.closePopup();
      } else if (slug !== state._state) {
        markers[slug].fireEvent('click');
      }
    });
  };


  // INIT

  createMap();
  autoUpdateControl.addTo(map);
  topRight.init();
  initLocationHash();


  // ***********
  // * EXPORTS *
  // ***********

  window.state = state;
  window.map = map;
  window.markers = markers;
  window.updateMap = updateMap;
  window.isoToDate = isoToDate;
  window.tzOffset = tzOffset;
  window.updated_at = updated_at;
})();
