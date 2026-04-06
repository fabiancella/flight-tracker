const map = L.map('map').setView([27.5, -82.0], 7 );

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

const markerLayer = L.layerGroup().addTo(map);

const planeIcon = L.icon({
    iconUrl: 'plane-icon.svg',
    iconSize: [30, 30],
    iconAnchor: [15, 15],
})

async function fetchTelemetry(){
    try{
        const response = await fetch ("http://100.48.102.102:8000/telemetry")

        if(!response.ok){
            throw new Error("Couldn't reach data")
        }
        const data = await response.json();
            console.log(data)
                
        markerLayer.clearLayers();

        for (const planes of data){
            const time = new Date(planes.timestamp + 'Z').toLocaleTimeString('en-US', {
                timeZone : 'America/New_York',
                month: '2-digit',
                day: '2-digit', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });

            // Plane physical marker    
            const plane_marker = L.marker([planes.latitude, planes.longitude], {
                icon: planeIcon,
                rotationAngle: planes.heading,
                rotationOrigin: 'center center'
            }).addTo(markerLayer);

            console.log(planes.heading)
        
            // Plane information popup
            plane_marker.bindPopup(`Callsign: ${planes.callsign}<br>Altitude: ${Math.round(planes.altitude_ft)} ft<br>Ground Speed: ${Math.round(planes.groundspeed_kt)} kts<br>Time: ${time}`);
        }
    }

    catch(error){
        console.log(error)
    }

}

async function fetchCallsign(){
    try{
        const callsign = document.getElementById('callsign-input').value;
        const response = await fetch (`http://100.48.102.102:8000/telemetry/callsign/${callsign}`)

        if(!response.ok){
            throw new Error("Callsign not found")
        }

        const data = await response.json();
        console.log(data)

        markerLayer.clearLayers();

    //     for (const planes of data){
    //         const time = new Date(planes.timestamp + 'Z').toLocaleTimeString('en-US', {
    //             timeZone : 'America/New_York',
    //             month: '2-digit',
    //             day: '2-digit', 
    //             year: 'numeric',
    //             hour: '2-digit',
    //             minute: '2-digit',
    //             hour12: false
    //         });

    //         const plane_marker = L.marker([planes.latitude, planes.longitude], {
    //             icon: planeIcon,
    //             rotationAngle: planes.heading,
    //             rotationOrigin: 'center center'
    //         }).addTo(markerLayer);

    //         plane_marker.bindPopup(`Callsign: ${planes.callsign}<br>Altitude: ${Math.round(planes.altitude_ft)} ft<br>Ground Speed: ${Math.round(planes.groundspeed_kt)} kts<br>Time: ${time}`);
    // }
        
        const latest = data[0]

        const time = new Date(latest.timestamp + 'Z').toLocaleTimeString('en-US', {
                timeZone : 'America/New_York',
                month: '2-digit',
                day: '2-digit', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });

        const plane_marker = L.marker([latest.latitude, latest.longitude], {
                icon: planeIcon,
                rotationAngle: latest.heading,
                rotationOrigin: 'center center'
            }).addTo(markerLayer);

        plane_marker.bindPopup(`Callsign: ${latest.callsign}<br>Altitude: ${Math.round(latest.altitude_ft)} ft<br>Ground Speed: ${Math.round(latest.groundspeed_kt)} kts<br>Time: ${time}`);

    }

     catch(error){
        console.log(error)
    }
}
document.getElementById('search-btn').addEventListener('click', fetchCallsign);
fetchTelemetry()
setInterval(fetchTelemetry, 300000)
