(function() {
    google.load('jquery', '1.4.2');
    google.load('jqueryui', '1.7.2');
    google.load('maps', '3', { other_params: 'key=AIzaSyDvrDCSfQxN9h5UCwLKJxrb5kBQyI7l0cc&libraries=visualization' });
    google.setOnLoadCallback(function() {
        window.company_latlng = new google.maps.LatLng(COMPANY_LATITUDE, COMPANY_LONGITUDE);
        window.currentCenter  = company_latlng;
        window.map            = new google.maps.Map(document.getElementById('map-canvas'), {
            center:             company_latlng,
            zoom:               13,
            mapTypeId:          google.maps.MapTypeId.ROADMAP,
            disableDefaultUI:   true
        });

        $(document).ready(function() {
            setupMap();
            setupSlider();
            setupForm();
            setupSidebar();
        });
    });

    setupMap = function() {
        var marker = new google.maps.Marker({
            position:   company_latlng,
            map:        window.map,
            icon:       ICON_LOCATION
        });
        google.maps.event.addListener(marker, 'click', function() {
            window.map.panTo(company_latlng)
        });

        google.maps.event.addListener(map, 'zoom_changed', function() {
            if (heatmap) {
                var radius = Math.max(HEATMAP_RADIUS * 20 / parseFloat(map.getZoom()), HEATMAP_RADIUS);
                heatmap.set('radius', radius);
            }
        });
    };

    setupSlider = function() {
        var updateDistance = function(min, max) {
            var minMile = parseFloat(min) / 100;
            var maxMile = parseFloat(max) / 100;
            $('#distance-text').text(minMile + ' miles - ' + maxMile + ' miles');
            $('#distance-input')
                .attr('data-min', minMile)
                .attr('data-max', maxMile);
        };
        $('#distance-slider').slider({
            range:  true,
            min:    MIN_DISTANCE,
            max:    MAX_DISTANCE,
            values: [MIN_DISTANCE, MAX_DISTANCE],
            slide:  function(event, ui) {
                updateDistance(ui.values[0], ui.values[1])
            }
        });
        updateDistance(MIN_DISTANCE, MAX_DISTANCE);

        var updatePriceRange = function(min, max) {
            $('#price-range-text').text('$' + min + ' - $' + max);
            $('#price-range-input')
                .attr('data-min', min)
                .attr('data-max', max);
        };
        $('#price-range-slider').slider({
            range:  true,
            min:    MIN_PRICE,
            max:    MAX_PRICE,
            values: [MIN_PRICE, MAX_PRICE],
            slide:  function(event, ui) {
                updatePriceRange(ui.values[0], ui.values[1]);
            }
        });
        updatePriceRange(MIN_PRICE, MAX_PRICE);
    };

    setupForm = function() {
        $('#filter').submit(function() {
            closeSidebar();
            return false;
        });
    };

    setupSidebar = function() {
        $('#expand-btn').click(function() {
            if ($('#st-container').hasClass('st-menu-open')) {
                closeSidebar();
            } else {
                openSidebar();
            }
            return false;
        });
    };

    var previousQuery = {
        distance: {
            min: -1,
            max: -1
        },
        price: {
            min: -1,
            max: -1
        },
        safety: -1
    };
    var heatmap     = null;
    var heatMapData = [];
    var markers     = [];

    closeSidebar = function() {
        var minDistance   = $('#distance-input').attr('data-min');
        var maxDistance   = $('#distance-input').attr('data-max');
        var minPriceRange = $('#price-range-input').attr('data-min');
        var maxPriceRange = $('#price-range-input').attr('data-max');
        var safety        = $('#safety').val();

        // wtf...
        if (minDistance != previousQuery.distance.min ||
            maxDistance != previousQuery.distance.max ||
            minPriceRange != previousQuery.price.min ||
            maxPriceRange != previousQuery.price.max ||
            safety != previousQuery.safety) {

            previousQuery.distance.min = minDistance;
            previousQuery.distance.max = maxDistance;
            previousQuery.price.min = minPriceRange;
            previousQuery.price.max = maxPriceRange;
            previousQuery.safety = safety;

            for (var i = markers.length - 1; i >= 0; i--) {
                markers[i].setMap(null);
            };
            markers = [];

            updateHeatmap();
            updateHousing();
        }

        $('#st-container').removeClass('st-menu-open');
    };

    openSidebar = function() {
        $('#st-container').addClass('st-menu-open');
    };

    updateHeatmap = function() {
        $('#loader').fadeIn();
        $.ajax({
            url:      '/api/weights',
            type:     'GET',
            dataType: 'json',
            data:     previousQuery,
            success: function(data) {
                for (var i = data.length - 1; i >= 0; i--) {
                    var point = data[i];
                    heatMapData.push({
                        location: new google.maps.LatLng(parseFloat(point.latitude), parseFloat(point.longitude)),
                        weight:   parseFloat(point.weight)
                    });
                };

                heatmap = new google.maps.visualization.HeatmapLayer({
                    data:     heatMapData,
                    map:      window.map,
                    radius:   HEATMAP_RADIUS
                })
                markers.push(heatmap);

                $('#loader').fadeOut();
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };

    updateHousing = function() {        
        $('#loader').fadeIn();
        $.ajax({
            url:      '/api/houses',
            type:     'GET',
            dataType: 'json',
            data:     previousQuery,
            success: function(data) {
                for (var i = data.length - 1; i >= 0; i--) {
                    var house = data[i];
                    var housingMarker = new google.maps.Marker({
                        map:      window.map,
                        position: new google.maps.LatLng(parseFloat(house.address.latitude), parseFloat(house.address.longitude)),
                        title:    '$' + house.price + ' at ' + house.address.street_address
                    });

                    (function(marker, house, i) {
                        // add click event
                        google.maps.event.addListener(marker, 'click', function() {
                            infowindow = new google.maps.InfoWindow({
                                content: '<strong>$' + house.price + '</strong><a href="' + house.source + '" class="external-link" target="_blank">Link</a>'
                            });
                            infowindow.open(map, marker);
                        });
                    })(housingMarker, house, i);

                    markers.push(housingMarker);
                };
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });
    };
})();