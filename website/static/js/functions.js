// Get API Key and load google map dynamically
function loadGoogleMaps() {
    fetch('http://127.0.0.1:5000/get_api_key')
        .then(response => response.json())
        .then(data => {
            const apiKey = data.api_key;
            const script = document.createElement('script');
            
            // 使用 loading=async 参数
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap&language=en&loading=async`;
            
            // 确保 async 和 defer 正确设置
            script.async = true;
            script.defer = true;

            // 添加 crossorigin 属性
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
        fetch('http://127.0.0.1:5000/stations') // Get station data
        .then(response => response.json()),
        fetch('http://127.0.0.1:5000/availability')// Get availability data
        .then(response => response.json())
    ]).then(([stations, availability]) => {
        // Create a map of availability data keyed by station number
        const availabilityMap = {};
        availability.forEach(item => {
            availabilityMap[item.number] = item;
        });
                
        addMarkers(stations,availabilityMap, map);
        })
        .catch(error => console.error("Error fetching station data:", error));
}



// mark at the map
function addMarkers(stations,availabilityMap,map) {
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

            // click on the marker to display info window
            marker.addListener("click", () => {
                infoWindow.open(map, marker);
            });
        }else {
            console.warn(`No availability data for station: ${station.number}`);
        }
    });
}
