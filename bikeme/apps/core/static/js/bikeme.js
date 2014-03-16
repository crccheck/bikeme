/* global $, L, d3, station_data: false */
(function () {
  'use strict';

  // Lets us turn json dates into javascript dates
  var isoToDate = d3.time.format('%Y-%m-%dT%H:%M:%SZ');
  var tzOffset = new Date().getTimezoneOffset() / -60;


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

    var xScale = d3.time.scale()
      .range([0, plotBox.width])
      .domain([
        Math.min(cleanedData.recent[0].date, cleanedData.yesterday[0].date),
        cleanedData.yesterday[cleanedData.yesterday.length - 1].date
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

  var showStandInfo = function (stand, latlng) {
    var popup = L.popup({
      // keep popup from cutting off chart
      maxWidth: 10000
    });
    var $paper = $('<div><h3>Bike Availability at ' + stand.name + '</h3>' +
      '<div>Bikes: <i>' + stand.bikes + '</i>' +
      ' Docks: <i>' + stand.docks + '</i>' +
      ' Status: <i>' + stand.status + '</i>' +
      '</div>' +
      '<div class="loading">Loading... <i class="fa fa-spinner fa-spin"></i></div>' +
      '</div>');
    $.getJSON(stand.url, function (data) {
      buildChart($paper, data);
      popup.setContent($paper[0]);
    });
    popup
      .setLatLng(latlng)
      .setContent($paper[0])
      .openOn(map);
  };


  // **************
  // * CREATE MAP *
  // **************

  var map = L.map('map', {
        // scrollWheelZoom: false
      }),
      bounds = [];

  var createMap = function () {
    $.each(station_data.stations, function (idx, stand) {
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
  };
  createMap();

  // **********
  // * LEGEND *
  // **********

  var legend = L.control({position: 'bottomleft'}),
      $legend = $('<div class="legend">Last Update: <span class="last"></span>s' +
        ' Next Update: <span class="next"></span></div>');
  legend.onAdd = function () {
    var $last = $legend.find('.last');
    var updated_at = d3.time.hour.offset(isoToDate.parse(station_data.updated_at), tzOffset);
    var _update = function () {
      var diff = (Date.now() - updated_at) / 1000;
      $last.text(Math.floor(diff));
    };
    _update();
    setInterval(_update, 1000);
    return $legend[0];
  };
  legend.addTo(map);

  // ***************
  // * GEOLOCATION *
  // ***************

  var myLocation = null;

  var zoomMap = function (position) {
    myLocation = L.latLng(position.coords.latitude, position.coords.longitude);
    if (!map.getBounds().contains(myLocation)) {
      // user's location is not worth panning to
      return;
    }
    map.panTo(myLocation);
    map.setZoom(16);
    L.marker(myLocation).addTo(map);
    map.addControl(new GoHomeControl());
  };

  var updatePosition = function (position) {
    myLocation = L.latLng(position.coords.latitude, position.coords.longitude);
    map.panTo(myLocation);
  };

  var GoHomeControl = L.Control.extend({
    options: {
      position: 'topright'
    },
    onAdd: function (map) {
      var container = L.DomUtil.create('div', 'leaflet-control-home leaflet-bar');
      // WISHLIST add system map button even if geolocation is off
      $(container).html(
        '<a class="action-all" href="#" title="View system map"><span class="fa fa-arrows-alt"></span></a>' +
        '<a class="action-home" href="#" title="Go home"><span class="fa fa-location-arrow"></span></a>'
        )
        .find('a.action-home').on('click', function (e) {
          e.preventDefault();
          navigator.geolocation.getCurrentPosition(updatePosition);
        }).end()
        .find('a.action-all').on('click', function (e) {
          e.preventDefault();
          map.fitBounds(bounds);
        });
      return container;
    }
  });

  navigator.geolocation.getCurrentPosition(zoomMap);


  // ***********
  // * EXPORTS *
  // ***********

  window.map = map;
  window.isoToDate = isoToDate;
  window.tzOffset = tzOffset;
})();
