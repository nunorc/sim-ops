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
			mqtt_status: "checking"
		}
	},
	methods: {
		updatePosition(data) {
			console.log('updatePosition');
			this.position = [data.x, data.y, data.z];
			this.lat_lon = [data.lat, data.lon]
			console.log(data);
		}

	},
	mounted() {
		// this.mqtt_status = this.$mqtt.status();

		// // subscribe to data topic to get updates
		// this.$mqtt.subscribe("opssat/data", (message) => {
		// 	let data = JSON.parse(JSON.parse(message));

		// 	if (data.topic === "position")
		// 		this.updatePosition(data.data);
		// }, false);
	}
}
</script>
<template>
	<!-- BEGIN page-header -->
	<h1 class="page-header">
		Operations <small>Execute Procedure</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<p>TODO</p>



</template>