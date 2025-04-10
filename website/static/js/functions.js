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

function displayStationInfo(station, availability) {
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
<<<<<<< HEAD
            },
            name: 'Current'
=======
            }
>>>>>>> 624e007b50b278b617473cea2cd77098ee5d52b2
        }];
        
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
        <div class="station-data">
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
                    <td>${station.position_lat.toFixed(6)}, ${station.position_lng.toFixed(6)}</td>
                </tr>
            </table>
<<<<<<< HEAD
            <div id="prediction-data" class="prediction-loading">
                <h4>Loading predictions...</h4>
                <div class="loading-spinner"></div>
            </div>
=======
>>>>>>> 624e007b50b278b617473cea2cd77098ee5d52b2
        </div>
    `;

    document.getElementById('station-details').innerHTML = infoHTML;
    
    // Make the station info section visible if it was hidden
    container.style.display = 'block';
<<<<<<< HEAD
    
    // Fetch prediction data
    fetchPrediction(station.number);
}

async function fetchPrediction(stationNumber) {
    const datetime = document.getElementById("datetime-picker").value;
    if (!datetime) {
        alert("Please select date and time.");
        return;
    }
    try {
        const response = await fetch(`/predict?station_id=${stationNumber}&datetime=${encodeURIComponent(datetime)}`);
        const prediction = await response.json();
        displayPrediction(prediction);
    } catch (error) {
        console.error("Prediction Fetch Error:", error);
        document.getElementById("prediction-data").innerHTML = "<p>Error loading prediction.</p>";
    }
}

function displayPrediction(prediction) {
    if (prediction.error) {
        document.getElementById("prediction-data").innerHTML = `<p>Error: ${prediction.error}</p>`;
        return;
    }
    const html = `
        <h4>Prediction:</h4>
        <ul>
            <li>In 30 minutes: ${prediction.in_30_min} bikes</li>
            <li>In 1 hour: ${prediction.in_1_hour} bikes</li>
        </ul>
    `;
    document.getElementById("prediction-data").innerHTML = html;
}

async function getWeather() {
    const res = await fetch('/weather', { method: 'POST' });
    const data = await res.json();
    console.log("Weather:", data.main.temp);
=======
>>>>>>> 624e007b50b278b617473cea2cd77098ee5d52b2
}