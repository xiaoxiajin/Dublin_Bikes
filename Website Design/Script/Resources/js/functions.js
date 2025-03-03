// Get API Key and load google map dynamically
function loadGoogleMaps() {
    fetch('http://127.0.0.1:5000/get_api_key')
        .then(response => response.json())
        .then(data => {
            const apiKey = data.api_key;
            const script = document.createElement('script');
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&language=en`;
            script.async = true;
            script.defer = true;
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
    getStations(map);
}

// Get station data and store into map and mark in the map
function getStations(map) {
    fetch('/stations') // Get station data from 
        .then(response => response.json())
        .then(data => {
            addMarkers(data, map);
        })
        .catch(error => console.error("Error fetching station data:", error));
}

// mark at the map
function addMarkers(stations, map) {
    stations.forEach(station => {
        const marker = new google.maps.Marker({
            position: { lat: station.position_lat, lng: station.position_long },
            map,
            title: station.address,
            icon: "Resources/purple_marker.svg"
        });

        // create a info window
        const infoWindow = new google.maps.InfoWindow({
            content: `<strong>${station.address}</strong><br>
                      <p>Bikes Available: ${station.available_bikes}</p>
                      <p>Stands Available: ${station.available_bike_stands}</p>`
        });

        // click on the marker to display info window
        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });
    });
}
