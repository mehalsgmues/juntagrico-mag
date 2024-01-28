function onEachFeature(feature, layer) {
    if (feature.properties && (feature.properties.url || feature.properties.name)) {
        let text = []
        if (feature.properties.name) {
            text.push('<strong>' + feature.properties.name + '</strong>')
        }
        if (feature.properties.url) {
            text.push('<a href="' + feature.properties.url + '">Einsatz öffnen</a>')
        }
        if (feature.properties.id) {
            text.push($('.map-popup-' + feature.properties.id).html())
        }
        if (text) {
            layer.bindPopup(text.join('<br>'));
        }
    }
}

$(document).ready(function () {
    $('.map-container').each(function() {
        let map = L.map(this, {fullscreenControl: true}).setView([48, 2], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            {
                attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                    '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
            }).addTo(map);
        let map_job_data_element = document.getElementById('map_job_data')
        if (map_job_data_element) {
            let map_job_data = JSON.parse(map_job_data_element.textContent)
            let geo_json
            if (Array.isArray(map_job_data)) {
                geo_json = L.geoJSON(map_job_data, {style: {color: "#000000"}}).addTo(map)
            } else {
                if (this.dataset.jobs) {
                    map_job_data = map_job_data[this.dataset.jobs]
                }
                if (map_job_data) {
                    if (!map_job_data.data) {
                        geo_json = L.geoJSON(map_job_data, {style: {color: "#000000"}}).addTo(map)
                    } else {
                        geo_json = L.geoJSON(map_job_data['data'], {
                            onEachFeature: onEachFeature,
                            style: function (feature) {
                                if (map_job_data.legend) {
                                    try {
                                        return {color: map_job_data.legend[feature.properties.status][1]}
                                    } catch {
                                        return {color: map_job_data.legend.default[1]}
                                    }
                                }
                                try {
                                    return {color: feature.properties.color}
                                } catch {}
                                return {}
                            }
                        }).addTo(map)
                    }
                }
            }

            if (geo_json) {
                map.fitBounds(geo_json.getBounds(), {padding: [100, 100]});
            }

            if (map_job_data && map_job_data.legend) {
                L.control.Legend({
                    position: "topright",
                    title: "Legende",
                    legends: Object.values(map_job_data.legend).map((x) => ({label: x[0], type: "rectangle", color: x[1]}))
                }).addTo(map);
            }
        }
    })
})