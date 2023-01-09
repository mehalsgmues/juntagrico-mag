function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.url) {
        layer.bindPopup('<strong>' + feature.properties.name + '</strong><br><a href="' + feature.properties.url + '">Einsatz öffnen</a>');
    }
}

define([], function () {
    $('#map-container').append('<div id="job-map">')
    let map = L.map('job-map', {fullscreenControl: true}).setView([48, 2], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
        }).addTo(map);
    let map_job_data_element = document.getElementById('map_job_data')
    if (map_job_data_element) {
        let map_job_data = JSON.parse(map_job_data_element.textContent)
        let geo_json = L.geoJSON(map_job_data, {
            onEachFeature: onEachFeature,
            style: function(feature) {
                switch (feature.properties.status) {
                    case 0: return {color: "#ff0000"};
                    case 100: return {color: "#00ff00"};
                    case 101: return {color: "#0000ff"};
                    case undefined: return {color: "#000000"};
                    default: return {color: "#ffff00"};
                }
            }
        }).addTo(map)
        map.fitBounds(geo_json.getBounds(), {padding: [100, 100]});

        if (Array.isArray(map_job_data)) {
            L.control.Legend({
                position: "topright",
                title: "Legende",
                legends: [
                    {label: "Deine Gebiete", type: "rectangle", color: "#0000ff"},
                    {label: "Offen",  type: "rectangle", color: "#ff0000"},
                    {label: "Vergeben/Erledigt", type: "rectangle", color: "#00ff00"},
                    {label: "Unterstützung Gesucht", type: "rectangle", color: "#ffff00"}
                ]
            }).addTo(map);
        }
    }
})