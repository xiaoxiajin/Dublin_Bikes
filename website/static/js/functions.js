// Get API Key and load google map dynamically
function loadGoogleMaps() {
    fetch('/get_api_key')
        .then(response => response.json())
        .then(data => {
            const apiKey = data.api_key;
            const script = document.createElement('script');
            
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&language=en&loading=async`;
            script.async = true;
            script.defer = true;
            script.crossOrigin = 'anonymous';

            script.onload = () => {
                console.log('Google Maps API loaded successfully');
            };
            
            script.onerror = (error) => {
                console.error('Failed to load Google Maps API', error);
            };

            document.head.appendChild(script);
        })
        .catch(error => console.error("Error fetching API key:", error));
}

// initialize map
function initMap() {
    const dublin = { lat: 53.3498, lng: -6.2603 }; // dublin city center
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: dublin
    });

    // Get station data and store into map
    getStationsAndAvailability(map);
}

// Get station data and store into map and mark in the map
function getStationsAndAvailability(map) {
    Promise.all([
        fetch('/stations')
        .then(response => response.json()),
        fetch('/availability')
        .then(response => response.json())
    ]).then(([stations, availability]) => {
        // Create a map of availability data keyed by station number
        const availabilityMap = {};
        availability.forEach(item => {
            availabilityMap[item.number] = item;
        });
                
        addMarkers(stations, availabilityMap, map);
        })
        .catch(error => console.error("Error fetching station data:", error));
}

// mark at the map
function addMarkers(stations, availabilityMap, map) {
    stations.forEach(station => {
        // Get availability based on station number
        const availability = availabilityMap[station.number];
        if(availability){
            const marker = new google.maps.Marker({
                position: { lat: station.position_lat, lng: station.position_lng },
                map,
                title: station.address,
                icon: "/static/img/available.png"
            });

            // create a info window
            const infoWindow = new google.maps.InfoWindow({
                content: `<div class="info-window">
                            <strong>${station.address}</strong><br>                        
                            <p class="bikes-available">Bikes Available: ${availability.available_bikes}</p>
                            <p class="stands-available">Stands Available: ${availability.available_bike_stands}</p>
                        </div>`
            });

            // click on the marker to display info window and show station details
            marker.addListener("click", () => {
                infoWindow.open(map, marker);
                displayStationInfo(station, availability);
            });
        
        } else {
            console.warn(`No availability data for station: ${station.number}`);
        }
    });
}

function clearCharts() {
    // clear Plotly charts
    const plotlyCharts = ['station-graph', 'station-pie-chart'];
    plotlyCharts.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            Plotly.purge(element);
        }
    });

    // clear Chart.js charts
    if (window.stationTrendChart) {
        window.stationTrendChart.destroy();
    }
    if (window.stationStandsChart) {
        window.stationStandsChart.destroy();
    }
}

function displayStationInfo(station, availability) {
    clearCharts();
    const container = document.getElementById("station-info");
    
    // Make sure Plotly is loaded
    if (typeof Plotly !== 'undefined') {
        // Plotly graph for bikes availability
        const graphData = [{
            x: ['Available Bikes', 'Available Bike Stands'],
            y: [availability.available_bikes, availability.available_bike_stands],
            type: 'bar',
            marker: {
                color: ['#7CC1D7', '#2c2c2c']
            },
            name: 'Current'
            }
        ];
        
        const layout = {
            title: `${station.address} - Live Availability`,
            xaxis: { title: 'Type' },
            yaxis: { title: 'Count' },
            margin: { t: 50, b: 50, l: 50, r: 50 }
        };
        
        Plotly.newPlot('station-graph', graphData, layout);

        // Create pie chart for percentage visualization
        const totalStands = station.bike_stands;
        const availableBikes = availability.available_bikes;
        const availableStands = availability.available_bike_stands;
        
        const pieData = [{
            values: [availableBikes, availableStands],
            labels: ['Available Bikes', 'Available Stands'],
            type: 'pie',
            marker: {
                colors: ['#7CC1D7', '#2c2c2c']
            },
            textinfo: 'percent',
            hole: 0.4
        }];
        
        const pieLayout = {
            title: 'Capacity Distribution',
            height: 300,
            margin: { t: 50, b: 30, l: 30, r: 30 }
        };
        
        Plotly.newPlot('station-pie-chart', pieData, pieLayout);
    } else {
        console.error("Plotly library is not loaded!");
    }

    // Format date nicely
    const lastUpdateDate = new Date(availability.last_update).toLocaleString();

    // Station info section with all the required fields
    const infoHTML = `
            <h3>Station Information</h3>
            <table class="info-table">
                <tr>
                    <th>Station Number</th>
                    <td>${station.number}</td>
                </tr>
                <tr>
                    <th>Name</th>
                    <td>${station.name}</td>
                </tr>
                <tr>
                    <th>Address</th>
                    <td>${station.address}</td>
                </tr>
                <tr>
                    <th>Status</th>
                    <td><span class="status-badge ${availability.status.toLowerCase()}">${availability.status}</span></td>
                </tr>
                <tr>
                    <th>Banking</th>
                    <td>${station.banking ? 'Yes' : 'No'}</td>
                </tr>
                <tr>
                    <th>Total Bike Stands</th>
                    <td>${station.bike_stands}</td>
                </tr>
                <tr>
                    <th>Available Bikes</th>
                    <td>${availability.available_bikes}</td>
                </tr>
                <tr>
                    <th>Available Stands</th>
                    <td>${availability.available_bike_stands}</td>
                </tr>
                <tr>
                    <th>Last Updated</th>
                    <td>${lastUpdateDate}</td>
                </tr>
                <tr>
                    <th>Coordinates</th>
                    <td>${station.position_lat.toFixed(2)}, ${station.position_lng.toFixed(2)}</td>
                </tr>
            </table>
            
            
            
        </div>
    `;
    
    
    document.getElementById('station-details').innerHTML = infoHTML;
    
    // Make the station info section visible if it was hidden
    container.style.display = 'block';
    
    // Fetch prediction data
    fetchStationTrend(station.number,station.bike_stands);
}


async function getWeather() {
    const res = await fetch('/weather', { method: 'POST' });
    const data = await res.json();
    // console.log("Weather:", data.main.temp);

    const temp = Math.round(data.main.temp);
    const description = data.weather[0].description;
    const iconCode = data.weather[0].icon;
    const iconUrl = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;

    const html = `
        <div class="weather-box">
            <img src="${iconUrl}" alt="${description}" class="weather-icon">
            <div class="weather-text">
                <span class="weather-temp">${temp}°C</span>
                <span class="weather-desc">${description}</span>
            </div>
        </div>
    `;

    document.getElementById("weather-display").innerHTML = html;
}

async function fetchStationTrend(stationId, totalStands) {
    try {
        // clean station id
        const cleanStationId = stationId.toString().split(':')[0];

        const response = await fetch(`/station_trend?station_id=${cleanStationId}`);
        
        // check response status
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(errorData)}`);
        }

        const trendData = await response.json();

        // check trend data is an array
        if (!Array.isArray(trendData)) {
            throw new Error('Trend data is not an array');
        }

        // calculate stands 
        const standsData = trendData.map(item => ({
            time: item.time,
            predicted_bikes: item.bike_count,
            available_stands: Math.max(0, totalStands - item.bike_count)
        }));

        // trend container for bikes and stands
        const bikesChartContainer = document.getElementById('bikesChart');
        const standsChartContainer = document.getElementById('standsChart');
        
        if (!bikesChartContainer || !standsChartContainer) {
            throw new Error('Chart containers not found');
        }

        const trendCtx = bikesChartContainer.getContext('2d');
        const standsCtx = standsChartContainer.getContext('2d');
        
        // destroy any existing charts
        if (window.stationTrendChart instanceof Chart) {
            window.stationTrendChart.destroy();
        }
        if (window.stationStandsChart instanceof Chart) {
            window.stationStandsChart.destroy();
        }

        // chart for available bikes trend
        window.stationTrendChart = new Chart(trendCtx, {
            type: 'bar',
            data: {
                labels: trendData.map(item => item.time || 'Unknown'),
                datasets: [{
                    label: `Predicted Bikes at Station ${cleanStationId}`,
                    data: trendData.map(item => item.bike_count || 0),
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Bikes'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Bike Availability Trend for Station ${cleanStationId}`
                    }
                }
            }
        });

        // chart for station stands
        window.stationStandsChart = new Chart(standsCtx, {
            type: 'bar',
            data: {
                labels: standsData.map(item => item.time || 'Unknown'),
                datasets: [{
                    label: `Available Stands at Station ${cleanStationId}`,
                    data: standsData.map(item => item.available_stands),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Available Stands'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: `Stands Availability Trend for Station ${cleanStationId}`
                    }
                }
            }
        });

    } catch (error) {
        console.error('Detailed Error fetching trend:', error);
        
        // error handling
        const errorMessage = error.message || 'Unknown error occurred';
        
        // display error
        let bikesErrorContainer = document.getElementById('station-bikes-trend-container');
        let standsErrorContainer = document.getElementById('station-stands-trend-container');
        
        if (bikesErrorContainer) {
            bikesErrorContainer.innerHTML = `
                <div class="trend-error">
                    <h4>Unable to Load Bikes Trend</h4>
                    <p>Error: ${errorMessage}</p>
                </div>
            `;
        }

        if (standsErrorContainer) {
            standsErrorContainer.innerHTML = `
                <div class="trend-error">
                    <h4>Unable to Load Stands Trend</h4>
                    <p>Error: ${errorMessage}</p>
                </div>
            `;
        }

        if (!bikesErrorContainer && !standsErrorContainer) {
            // alert when unable to load
            alert(`Unable to load station trend: ${errorMessage}`);
        }
    }
}

window.addEventListener('resize', function() {
    if (window.stationTrendChart) {
      window.stationTrendChart.resize();
    }
    if (window.stationStandsChart) {
      window.stationStandsChart.resize();
    }
  });