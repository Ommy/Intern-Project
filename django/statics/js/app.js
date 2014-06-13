(function() {
    google.load('jquery', '1.4.2');
    google.load('jqueryui', '1.7.2');
    google.load('maps', '3', { other_params: 'key=AIzaSyDvrDCSfQxN9h5UCwLKJxrb5kBQyI7l0cc&libraries=visualization' });
    google.setOnLoadCallback(function() {
        window.company_latlng = new google.maps.LatLng(COMPANY_LATITUDE, COMPANY_LONGITUDE);
        window.currentCenter  = company_latlng;
        window.map            = new google.maps.Map(document.getElementById('map-canvas'), {
            center:             company_latlng,
            zoom:               14,
            mapTypeId:          google.maps.MapTypeId.ROADMAP,
            disableDefaultUI:   true
        });

        $(document).ready(function() {
            addCompanyMarker();
            setupSlider();
            setupForm();
            setupSidebar();
        });
    });

    addCompanyMarker = function() {
        var marker = new google.maps.Marker({
            position:   company_latlng,
            map:        window.map,
            icon:       ICON_LOCATION
        });
        google.maps.event.addListener(marker, 'click', function() {
            window.map.panTo(company_latlng)
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
        priceRange: {
            min: -1,
            max: -1
        },
        safety: -1
    };

    closeSidebar = function() {
        $('#loader').fadeIn();

        var minDistance   = $('#distance-input').attr('data-min');
        var maxDistance   = $('#distance-input').attr('data-max');
        var minPriceRange = $('#price-range-input').attr('data-min');
        var maxPriceRange = $('#price-range-input').attr('data-max');
        var safety        = $('#safety').val();

        // wtf...
        if (minDistance == previousQuery.distance.min &&
            maxDistance == previousQuery.distance.max &&
            minPriceRange == previousQuery.priceRange.min &&
            maxPriceRange == previousQuery.priceRange.max &&
            safety == previousQuery.safety) {
            $('#st-container').removeClass('st-menu-open');
            $('#loader').fadeOut();
            return;
        } else {
            previousQuery.distance.min = minDistance;
            previousQuery.distance.max = maxDistance;
            previousQuery.priceRange.min = minPriceRange;
            previousQuery.priceRange.max = maxPriceRange;
            previousQuery.safety = safety;
        }

        $.ajax({
            url:        '/api/weights',
            type:       'GET',
            dataType:   'json',
            data: {
                distance: {
                    min: minDistance,
                    max: maxDistance
                },
                price: {
                    min: minPriceRange,
                    max: maxPriceRange
                },
                safety:  safety
            },
            success: function(data) {
                $('#loader').fadeOut();
                var heatMapData = [];
                for (var i = data.length - 1; i >= 0; i--) {
                    var point = data[i];
                    heatMapData.push({
                        location: new google.maps.LatLng(parseFloat(point.latitude), parseFloat(point.longitude)),
                        weight:   parseFloat(point.weight)
                    });
                };
                var heatmap = new google.maps.visualization.HeatmapLayer({
                    data:    heatMapData,
                    map:     window.map,
                    radius:  100,
                    gradient: [
                        'rgba(0,   255, 255, 0)',
                        'rgba(0,   255, 255, 1)',
                        'rgba(0,   191, 255, 1)',
                        'rgba(0,   127, 255, 1)',
                        'rgba(0,   63,  255, 1)',
                        'rgba(0,   0,   255, 1)',
                        'rgba(0,   0,   223, 1)',
                        'rgba(0,   0,   191, 1)',
                        'rgba(0,   0,   159, 1)',
                        'rgba(0,   0,   127, 1)',
                        'rgba(63,  0,   91,  1)',
                        'rgba(127, 0,   63,  1)',
                        'rgba(191, 0,   31,  1)',
                        'rgba(255, 0,   0,   1)'
                    ].reverse()
                });
                console.log(heatMapData);
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log(textStatus);
            }
        });

        $('#st-container').removeClass('st-menu-open');
    };

    openSidebar = function() {
        $('#st-container').addClass('st-menu-open');
    };

/*
    clearMarkers = function () {
        for (var i = markers.length - 1; i >= 0; i--) {
            markers[i].setMap(null);
        };
    };

    isCompanySet = function() {
        return parseInt($('#company').val()) != -1;
    };

    isDistanceSet = function() {
        return parseInt($('#distance').val()) != -1;
    };

    getCompanies = function() {
        $.ajax({
            url: '/map/search/all',
            success: function (company) {
                var container = $('#company');
                for (var i = company.length - 1; i >= 0; i--) {
                    var newOption = $('<option>');
                    newOption.attr({
                        'value':        company[i].id,
                        'data-addr':    company[i].location,
                        'data-lat':     company[i].lat,
                        'data-lng':     company[i].long
                    });
                    newOption.text(company[i].name)

                    container.append(newOption);
                };
            },
            error: function(xhr, textStatus, errorThrown) {
                alert(textStatus);
            }
        });
    };

    updateCompany = function() {
        if (parseInt($('#company').val()) != -1)
        {
            // set center
            var selected = $('#company').find('option:selected');
            var lat      = parseFloat(selected.attr('data-lat'));
            var lng      = parseFloat(selected.attr('data-lng'));

            currentCenter = new google.maps.LatLng(lat, lng);   
        }
        else 
        {
            currentCenter = toronto;
        }
        
        updateDistance();
    };

    updateDistance = function() {
        var newZoom  = 13;
        var distance = parseInt($('#distance').val());

        if (distance <= 1)
        {
            newZoom = 15;
        }
        else if (distance > 1 && distance <= 3)
        {
            newZoom = 14;
        }
        else if (distance > 3 && distance <= 5)
        {
            newZoom = 13
        }
        else if (distance > 5 && distance <= 10)
        {
            newZoom = 12;
        }
        else 
        {
            newZoom = 11;
        }

        map.setCenter(currentCenter);
        map.setZoom(newZoom);
        updateMarkers();
    };

    updateMarkers = function() {
        clearMarkers();

        if (isCompanySet() && isDistanceSet())
        {
            var distance    = parseInt($('#distance').val()); // user specified radius in kilometers

            // circle
            var radius      = distance * 1000; // maps API require circle radius in meters
            var companyArea = new google.maps.Circle({
                center:         currentCenter,
                clickable:      false,
                fillColor:      '#333',
                fillOpacity:    0.1,
                map:            map,
                strokeColor:    '#333',
                strokeOpacity:  0.4,
                strokeWeight:   1,
                radius:         radius
            });

            // center point marker
            var companyName = $('#company option:selected').text();
            var companyAddr = $('#company option:selected').attr('data-addr');
            var companyMarker = new google.maps.Marker({
                map:            map,
                position:       currentCenter,
                title:          companyName
            });
            var infowindow = new google.maps.InfoWindow({
                content: '<strong style='display:block'>' + companyName + '</strong><span style='display:block'>' + companyAddr + '</span>'
            });
            google.maps.event.addListener(companyMarker, 'click', function() {
                infowindow.open(map, companyMarker);
            });

            $.ajax({
                url:            '/map/search',
                data: {
                    company:    parseInt($('#company').val()),
                    distance:   distance
                },
                success: function(data) {
                    // living cost
                    var costAverage = data.avg;
                    var costOutput  = $('<li class='cost'>');
                    costOutput.append('The average monthly rent of living <span>' + distance + ' km</span> from <span>' + companyName + '</span> is:')
                    costOutput.append('<strong>$' + costAverage.toFixed(2) + '</strong>');
                    $('#app ul').find('.cost').remove();
                    $('#app ul').append(costOutput);

                    // heatmap
                    var heatMapData = [];
                    var houses = data.houses;
                    for (var i = houses.length - 1; i >= 0; i--) {
                        heatMapData.push({
                            location:   new google.maps.LatLng(parseFloat(houses[i].lat), parseFloat(houses[i].long)),
                            weight:     houses[i].price / costAverage
                        });
                    };
                    var heatmap = new google.maps.visualization.HeatmapLayer({
                        data:       heatMapData,
                        map:        map,
                        radius:     Math.max(40 / distance, 15)
                    });
                    markers.push(heatmap);
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert(textStatus);
                }
            });

            markers.push(companyArea);
            markers.push(companyMarker);
        }
    };
*/
})();