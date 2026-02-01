// js/map.js

const KOCHI_CENTER = [9.9312, 76.2673];
let map = null;
let currentMarker = null;

function initMap() {
    map = L.map('map').setView(KOCHI_CENTER, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

function updateMapMarker(lat, lon) {
    if (!map) initMap();

    // Remove existing marker
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }

    // Add new marker
    currentMarker = L.marker([lat, lon]).addTo(map);

    // Center map
    map.setView([lat, lon], 14);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', initMap);
