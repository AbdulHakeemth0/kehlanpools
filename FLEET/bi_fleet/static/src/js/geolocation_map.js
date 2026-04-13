/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { CharField, charField } from "@web/views/fields/char/char_field";
import { useRef, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";

/**
 * GeoLocationMap class extends CharField to provide a map with geolocation features.
 */
export class GeoLocationMap extends CharField {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.mapContainerRef = useRef('mapContainer');
        this.state = useState({
            latitude: '51.505',
            longitude: '-0.09',
            address: '',
            currentMarker: null,
        });

        // Bind the input field to the address state and handle address change
        this.handleAddressChange = this.handleAddressChange.bind(this);

        onMounted(() => this._initializeMap());
    }

    // Handle address changes when typing
    async handleAddressChange(event) {
        const newAddress = event.target.value;
        this.state.address = newAddress;

        if (newAddress) {
            await this.getLatLngFromAddress(newAddress);
            this._updateMap();
        }
    }

    /**
     * Initializes the Leaflet map and sets up event handlers.
     */
    async _initializeMap() {
        const mapContainer = this.mapContainerRef.el;
        const value = this.input.el.value;

        if (value) {
            await this.getLatLngFromAddress(value);
        }

        if (!mapContainer) {
            console.error('Map container not found.');
            return;
        }

        this.map = L.map(mapContainer, { zoomControl: true, zoom: 13, zoomAnimation: false, fadeAnimation: true, markerZoomAnimation: true })
            .setView([this.state.latitude, this.state.longitude], 13);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 15 }).addTo(this.map);

        this.state.currentMarker = L.marker([this.state.latitude, this.state.longitude])
            .addTo(this.map)
            .bindPopup('Selected Location')
            .openPopup();

        // Handle map clicks
        this.map.on('click', async (event) => {
            const { lat, lng } = event.latlng;
            this.state.latitude = lat;
            this.state.longitude = lng;
            try {
                const address = await this.getAddressFromLatLng(lat, lng);
                this.state.address = address;
                await this.props.record.update({ [this.props.name]: address });
            } catch (error) {
                console.error('Error fetching address:', error);
            }

            if (this.state.currentMarker) {
                this.map.removeLayer(this.state.currentMarker);
            }
            const newMarker = L.marker([lat, lng])
                .addTo(this.map)
                .bindPopup('Selected Location')
                .openPopup();
            this.state.currentMarker = newMarker;
        });
    }

    /**
     * Updates the map view based on current state.
     */
    _updateMap() {
        if (this.state.address) {
            this.map.setView([this.state.latitude, this.state.longitude], 13);
            if (this.state.currentMarker) {
                this.map.removeLayer(this.state.currentMarker);
            }
            this.state.currentMarker = L.marker([this.state.latitude, this.state.longitude])
                .addTo(this.map)
                .bindPopup('Selected Location')
                .openPopup();
        }
    }

    async getAddressFromLatLng(latitude, longitude) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`);
            const data = await response.json();
            return `${data.address.village || ''}, ${data.address.county || ''}, ${data.address.state || ''}, ${data.address.country || ''}`;
        } catch (error) {
            console.error('Error fetching address:', error);
            return null;
        }
    }

    async getLatLngFromAddress(address) {
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`);
            const data = await response.json();
            if (data.length > 0) {
                this.state.latitude = parseFloat(data[0].lat);
                this.state.longitude = parseFloat(data[0].lon);
            }
        } catch (error) {
            console.error('Error fetching coordinates:', error);
        }
    }

    async _OpenMapview() {
        const { longitude, latitude } = this.state;
        if (latitude && longitude) {
            window.open(`https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`, '_blank');
        }
    }
}

GeoLocationMap.template = 'GeoLocation';
export const geoLocationMap = {
    ...charField,
    component: GeoLocationMap,
    displayName: _t("GeoLocation Map Viewer"),
};
registry.category("fields").add("geolocation_map", geoLocationMap);
