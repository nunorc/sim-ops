<script>
import { useAppVariableStore } from '@/stores/app-variable';
import apexchart from '@/components/plugins/Apexcharts.vue';
import jsVectorMap from 'jsvectormap';
import 'jsvectormap/dist/maps/world.js';
import 'jsvectormap/dist/css/jsvectormap.min.css';

const appVariable = useAppVariableStore();

export default {
	components: {
		apexchart: apexchart
	},
	data() {
		return {
			renderComponent: true,
			position: ['_', '_', '_'],
			lat_lon: ['_', '_'],
			markers: [],
			last_update: '_',
			mqtt_status: "checking"
		}
	},
	methods: {
		updatePosition(data) {
			console.log('updatePosition');
			this.position = [data.x, data.y, data.z];
			this.lat_lon = [data.lat, data.lon];
			this.renderMap(this.markers.concat([{ name: 'OPS-SAT', coords: [data.lat, data.lon] }]));
			this.markers.push({ name: '', coords: [data.lat, data.lon] });
			this.last_update = data.ts.split('.')[0].replace('T', ' ');
		},
		renderMap(markers) {
			document.getElementById('map-container').innerHTML = '<div id="map" style="height: 300px;"></div>';
			console.log('renderMap');
			console.log(markers);

			var map = new jsVectorMap({
				selector: '#map',
				map: 'world',
				zoomButtons: true,
				normalizeFunction: 'polynomial',
				hoverOpacity: 0.5,
				hoverColor: false,
				zoomOnScroll: false,
				series: {
					regions: [{
						normalizeFunction: 'polynomial'
					}]
				},
				labels: {
					markers: {
						render: (marker) => marker.name
					}
				},
				focusOn: {
					x: 0.5,
					y: 0.5,
					scale: 1
				},
				markers: markers,
				markerStyle: {
					initial: {
						fill: appVariable.color.theme,
						stroke: 'none',
						r: 1,
					},
					hover: {
						fill: appVariable.color.theme
					}
				},
				markerLabelStyle: {
					initial: {
						fontFamily: appVariable.font.bodyFontFamily,
						fontSize: '12px',
						fill: 'rgba('+ appVariable.color.inverseRgb + ', .75)'
					},
				},
				regionStyle: {
					initial: {
						fill: appVariable.color.inverse,
						fillOpacity: 0.25,
						stroke: 'none',
						strokeWidth: 0.4,
						strokeOpacity: 1
					},
					hover: {
						fillOpacity: 0.5
					}
				},
				backgroundColor: 'transparent',
			});
		}

	},
	mounted() {
		this.renderMap([]);

		this.mqtt_status = this.$mqtt.status();

		// subscribe to data topic to get updates
		this.$mqtt.subscribe("opssat/data", (message) => {
			let data = JSON.parse(JSON.parse(message));

			if (data.topic === "position")
				this.updatePosition(data.data);
		}, false);
	}
}
</script>
<template>
	<!-- BEGIN page-header -->
	<h1 class="page-header">
		Position <small class="float-end">
			<span class="badge bg-dark">MQTT</span>
			<span v-bind:class="{ 'badge': true, 'bg-success': mqtt_status == 'connected', 'bg-danger': mqtt_status != 'connected' }">{{ mqtt_status }}</span>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<!-- BEGIN row -->
	<div class="row" v-if="renderComponent">
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">X</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ position[0] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Y</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ position[1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Z</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ position[2] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>
	<!-- END row -->

	<div class="row" v-if="renderComponent">
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Latitude</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ lat_lon[0] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Longitude</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ lat_lon[1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Last Update</span>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ last_update }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-8 col-lg-8">
			<card class="mb-3">
				<card-body>
					<div id="map-container"></div>
				</card-body>
			</card>
		</div>
	</div>

</template>