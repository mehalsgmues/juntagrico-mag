/**
 * Edit map: edit, add and delete the areas (geo_area) of MapJobs using Leaflet.draw.
 *
 * - Clicking an area starts editing it (drag the vertices) and opens a popup to rename, delete or cancel it.
 * - Changes to the vertices are saved automatically (throttled).
 * - Clicking the map background leaves the editing mode.
 */
(function ($) {
    'use strict';

    var API_URL = '/map/api/job/';
    var AUTOSAVE_INTERVAL = 2000; // ms

    var AREA_STYLE = {color: '#000000', weight: 4, fillOpacity: 0.3, opacity: 1};
    var SELECTED_AREA_STYLE = {color: '#006400', fillOpacity: 0.3};
    var DRAWING_STYLE = {color: '#006400', weight: 2, fillColor: '#006400', fillOpacity: 0.3};

    var ADD_AREA_LABEL = '<i class="bi bi-plus-circle"></i> Neues Gebiet hinzufügen';
    var STOP_DRAWING_LABEL = '<i class="bi bi-x-circle"></i> Zeichnen abbrechen';

    var map = null;
    var editToolbar = null; // Leaflet.draw edit handler, used programmatically (without toolbar)
    var polygonHandler = null; // Leaflet.draw handler while drawing a new area
    var drawnItems = L.featureGroup(); // all areas that are not being edited
    var editableLayers = L.featureGroup(); // contains only the area that is being edited
    var currentEditLayer = null;
    var autosaveTimer = null;
    var lastAutosaveTime = 0;
    var hasAutosaved = false; // the current editing session has been (at least partly) saved

    /* ---------- Helpers ---------- */

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : null;
    }

    function apiPost(path, data) {
        return $.ajax({
            url: API_URL + path,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data || {}),
            headers: {'X-CSRFToken': getCookie('csrftoken')}
        });
    }

    function showError(message) {
        $('#messageModalMessage').text(message);
        $('#messageModal').modal('show');
    }

    /**
     * Create an error callback for a failed request that shows the error from the server.
     */
    function requestFailed(prefix) {
        return function (xhr) {
            showError(prefix + (xhr.responseJSON && xhr.responseJSON.error || xhr.statusText));
        };
    }

    /**
     * Ask the user to confirm an action in a modal.
     * @returns {Promise<boolean>} resolves with true if confirmed, false otherwise
     */
    function showConfirmModal(title, message, confirmText, confirmClass) {
        var modal = $('#confirmModal');
        var confirmButton = $('#confirmModalBtn');
        $('#confirmModalTitle').text(title);
        $('#confirmModalMessage').text(message);
        confirmButton.text(confirmText).removeClass('btn-danger btn-warning').addClass(confirmClass);
        return new Promise(function (resolve) {
            var confirmed = false;
            confirmButton.off('click').one('click', function () {
                confirmed = true;
                modal.modal('hide');
            });
            modal.one('hidden.bs.modal', function () {
                resolve(confirmed);
            });
            modal.modal('show');
        });
    }

    function fitToAreas() {
        if (drawnItems.getLayers().length > 0) {
            map.fitBounds(drawnItems.getBounds(), {padding: [50, 50]});
        }
    }

    /* ---------- Saving ---------- */

    function saveGeoArea(layer, name) {
        return apiPost(layer._mapJobId + '/save_geo_area/', {geo_area: layer.toGeoJSON(), name: name})
            .fail(requestFailed('Fehler beim Speichern: '));
    }

    function saveName(layer, newName) {
        return saveGeoArea(layer, newName).done(function () {
            layer._mapJobName = newName;
        });
    }

    function createMapJob(layer, typeId, name) {
        apiPost('create/', {geo_area: layer.toGeoJSON(), type_id: typeId, name: name})
            .done(function (response) {
                layer._mapJobId = response.job_id;
                layer._mapJobName = response.name;
                layer.setStyle(AREA_STYLE);
                setupLayerEvents(layer);
                fitToAreas();
            })
            .fail(function (xhr) {
                drawnItems.removeLayer(layer);
                requestFailed('Fehler beim Erstellen: ')(xhr);
            });
    }

    /**
     * Save the geometry of the area that is being edited. Called throttled while vertices are dragged.
     */
    function autosave() {
        autosaveTimer = null;
        if (!currentEditLayer) return;
        lastAutosaveTime = Date.now();
        hasAutosaved = true;
        saveGeoArea(currentEditLayer, currentEditLayer._mapJobName);
    }

    function scheduleAutosave() {
        if (!currentEditLayer || autosaveTimer) return; // a pending save will use the latest geometry
        var wait = Math.max(0, AUTOSAVE_INTERVAL - (Date.now() - lastAutosaveTime));
        autosaveTimer = setTimeout(autosave, wait);
    }

    /* ---------- Editing mode ---------- */

    function startEdit(layer) {
        cancelEdit();
        currentEditLayer = layer;
        hasAutosaved = false;
        drawnItems.removeLayer(layer);
        editableLayers.addLayer(layer);
        editToolbar.enable();
    }

    /**
     * Leave the editing mode. Changes that were not saved yet are reverted,
     * unless they were just flushed by a pending autosave.
     */
    function cancelEdit() {
        var layer = currentEditLayer;
        if (!layer) return;
        if (autosaveTimer) {
            clearTimeout(autosaveTimer);
            autosave();
        }
        if (!hasAutosaved) {
            editToolbar.revertLayers();
        }
        stopEdit(layer);
        drawnItems.addLayer(layer);
    }

    /**
     * Stop editing the layer without reverting any changes.
     */
    function stopEdit(layer) {
        editToolbar.disable();
        layer.setStyle(AREA_STYLE);
        editableLayers.removeLayer(layer);
        currentEditLayer = null;
        hasAutosaved = false;
    }

    /**
     * Remove an area from the map, e.g. after it was deleted or canceled.
     */
    function removeArea(layer) {
        if (currentEditLayer === layer) {
            clearTimeout(autosaveTimer);
            autosaveTimer = null;
            stopEdit(layer);
        }
        drawnItems.removeLayer(layer);
        map.closePopup();
    }

    function deleteMapJob(layer) {
        showConfirmModal(
            'Löschen bestätigen',
            'Möchtest du das Gebiet "' + layer._mapJobName + '" wirklich löschen?',
            'Löschen', 'btn-danger'
        ).then(function (confirmed) {
            if (!confirmed) return;
            apiPost(layer._mapJobId + '/delete/')
                .done(function () {
                    removeArea(layer);
                })
                .fail(requestFailed('Fehler beim Löschen: '));
        });
    }

    function cancelMapJob(layer) {
        showConfirmModal(
            'Absagen bestätigen',
            'Möchtest du das Gebiet "' + layer._mapJobName + '" wirklich absagen?',
            'Absagen', 'btn-warning'
        ).then(function (confirmed) {
            if (!confirmed) return;
            apiPost(layer._mapJobId + '/cancel/')
                .done(function () {
                    // canceled areas are not shown on the maps
                    removeArea(layer);
                })
                .fail(requestFailed('Fehler beim Absagen: '));
        });
    }

    /* ---------- Popup ---------- */

    /**
     * Name of the area that turns into an input when clicked.
     */
    function buildNameEditor(layer) {
        var row = $('<div class="popup-name-row"></div>');
        var nameSpan = $('<span class="popup-name-text"></span>');
        var pencilBtn = $('<span class="popup-name-pencil" title="Name bearbeiten"></span>').html('<i class="bi bi-pencil"></i>');

        function showName() {
            nameSpan.text(layer._mapJobName);
            row[0].innerHTML = '';
            row.append(nameSpan, pencilBtn);
        }

        // Use event delegation on row so the handler survives showName() re-renders
        row.on('click', '.popup-name-pencil', function (e) {
            e.stopPropagation();
            if (row.find('input').length) return;
            var input = $('<input type="text" class="form-control form-control-sm popup-name-input" />')
                .val(layer._mapJobName);
            row[0].innerHTML = '';
            row.append(input);
            input.focus().select();

            function finish(save) {
                input.off();
                var newName = input.val().trim();
                if (save && newName && newName !== layer._mapJobName) {
                    input.prop('disabled', true);
                    saveName(layer, newName).always(showName);
                } else {
                    showName();
                }
            }

            input.on('keydown', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    finish(true);
                } else if (e.key === 'Escape') {
                    finish(false);
                }
            });
            input.on('blur', function () {
                finish(true);
            });
        });

        showName();
        return row;
    }

    function buildPopupContent(layer, info) {
        var content = $('<div class="area-popup"></div>').append(buildNameEditor(layer));

        if (info.member_names.length > 0) {
            var members = $('<div class="area-popup-members"></div>')
                .append('<div class="font-weight-bold">Angemeldet:</div>');
            $.each(info.member_names, function (idx, memberName) {
                members.append($('<div class="pl-1"></div>').text('• ' + memberName));
            });
            content.append(members);
        }

        // Areas with assignments cannot be deleted, only canceled.
        var button = info.assignment_count > 0
            ? $('<button type="button" class="btn btn-sm btn-warning">Absagen</button>').on('click', function () {
                cancelMapJob(layer);
            })
            : $('<button type="button" class="btn btn-sm btn-danger">Löschen</button>').on('click', function () {
                deleteMapJob(layer);
            });
        return content.append($('<div class="mt-2"></div>').append(button))[0];
    }

    function openAreaPopup(layer, info) {
        L.popup()
            .setLatLng(layer.getBounds().getCenter())
            .setContent(buildPopupContent(layer, info))
            .openOn(map);
    }

    /**
     * Popup to enter the name of a newly drawn area. The area is discarded if the popup is closed without saving.
     */
    function promptNewAreaName(layer, typeId) {
        var saved = false;
        var input = $('<input type="text" class="form-control form-control-sm" value="Neues Gebiet" />');
        var saveButton = $('<button type="button" class="btn btn-sm btn-primary btn-block mt-2">Speichern</button>');
        var cancelButton = $('<button type="button" class="btn btn-sm btn-secondary btn-block mt-1">Abbrechen</button>');
        var content = $('<div></div>')
            .append('<label class="font-weight-bold d-block mb-1">Name des Gebiets:</label>')
            .append(input, saveButton, cancelButton);

        function save() {
            saved = true;
            map.closePopup();
            createMapJob(layer, typeId, input.val().trim() || 'Neues Gebiet');
        }

        saveButton.on('click', save);
        cancelButton.on('click', function () {
            map.closePopup();
        });
        input.on('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                save();
            }
        });

        var popup = L.popup({closeOnClick: false})
            .setLatLng(layer.getBounds().getCenter())
            .setContent(content[0]);
        popup.on('remove', function () {
            if (!saved) {
                drawnItems.removeLayer(layer);
            }
        });
        popup.openOn(map);
        input.focus().select();
    }

    /* ---------- Map ---------- */

    /**
     * Register the click handler of an area (MapJob). Requires _mapJobId and _mapJobName to be set on the layer.
     */
    function setupLayerEvents(layer) {
        layer.on('click', function (e) {
            // do not bubble to the map, which would leave the editing mode
            L.DomEvent.stopPropagation(e);
            if (currentEditLayer !== layer) {
                startEdit(layer);
            }
            $.getJSON(API_URL + layer._mapJobId + '/info/').then(
                function (info) {
                    openAreaPopup(layer, info);
                },
                requestFailed('Fehler beim Laden des Gebiets: ')
            );
        });
    }

    function loadAreas() {
        var mapJobData = JSON.parse(document.getElementById('map_job_data').textContent);
        L.geoJSON(mapJobData.data, {
            style: function () {
                return AREA_STYLE;
            },
            onEachFeature: function (feature, layer) {
                layer._mapJobId = feature.properties.id;
                layer._mapJobName = feature.properties.name || 'Unbenannt';
                setupLayerEvents(layer);
                drawnItems.addLayer(layer);
            }
        });
        fitToAreas();
    }

    function setAddAreaButtonState(button, drawing) {
        $(button).html(drawing ? STOP_DRAWING_LABEL : ADD_AREA_LABEL).toggleClass('drawing-mode', drawing);
    }

    /**
     * Leaflet control with the button to start and stop drawing a new area.
     */
    var AddAreaControl = L.Control.extend({
        options: {position: 'topleft'},
        onAdd: function () {
            var container = L.DomUtil.create('div', 'add-area-control');
            setAddAreaButtonState(container, false);
            L.DomEvent.disableClickPropagation(container);
            L.DomEvent.on(container, 'click', function () {
                if (polygonHandler) {
                    polygonHandler.disable();
                } else {
                    cancelEdit();
                    map.closePopup();
                    polygonHandler = new L.Draw.Polygon(map, {
                        allowIntersection: false,
                        showArea: true,
                        shapeOptions: DRAWING_STYLE
                    });
                    polygonHandler.enable();
                }
            });
            return container;
        }
    });

    function initEditMap() {
        var container = $('.map-container');
        if (!container.length) return;
        var typeId = container.data('type-id');

        // The default zoom and fullscreen controls are added below the "add area" button.
        map = L.map(container[0], {zoomControl: false, fullscreenControl: false}).setView([48, 2], 11);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>'
        }).addTo(map);
        editableLayers.addTo(map);
        drawnItems.addTo(map);
        loadAreas();

        // Programmatic editing, see https://github.com/Leaflet/Leaflet.draw/issues/129
        editToolbar = new L.EditToolbar.Edit(map, {
            featureGroup: editableLayers,
            selectedPathOptions: SELECTED_AREA_STYLE
        });

        // EDITVERTEX fires continuously while a vertex is dragged
        map.on(L.Draw.Event.EDITVERTEX, scheduleAutosave);

        map.on(L.Draw.Event.CREATED, function (event) {
            drawnItems.addLayer(event.layer);
            promptNewAreaName(event.layer, typeId);
        });
        map.on(L.Draw.Event.DRAWSTART, function () {
            setAddAreaButtonState('.add-area-control', true);
        });
        map.on(L.Draw.Event.DRAWSTOP, function () {
            polygonHandler = null;
            setAddAreaButtonState('.add-area-control', false);
        });

        // Leave the editing mode when clicking the map background
        map.on('click', function () {
            if (currentEditLayer) {
                cancelEdit();
                map.closePopup();
            }
        });

        new AddAreaControl().addTo(map);
        L.control.zoom({position: 'topleft'}).addTo(map);
        L.control.fullscreen({position: 'topleft'}).addTo(map);
    }

    $(document).ready(initEditMap);

})(jQuery);
