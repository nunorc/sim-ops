<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import apexchart from '@/components/plugins/Apexcharts.vue';
import chartjs from '@/components/plugins/Chartjs.vue';
import jsVectorMap from 'jsvectormap';
import 'jsvectormap/dist/maps/world.js';
import 'jsvectormap/dist/css/jsvectormap.min.css';
import axios from 'axios';

const appVariable = useAppVariableStore(),
      appOption = useAppOptionStore();

export default {
	components: {
		chartjs: chartjs,
		apexchart: apexchart
	},
	data() {
		return {
			renderComponent: true,
			loading: false,
			config: null,
			state: null,
			ts: -1,
			dt: '_',
			chartIMUx: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'IMU x', data: [] }]
			},
			chartIMUy: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'IMU y', data: [] }]
			},
			chartIMUz: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'IMU z', data: [] }]
			},
			mqtt_status: "checking"
		}
	},
	methods: {
		updateData(data) {
			this.loading = false;
			this.config = data.config;
			this.state = data.state;
			this.ts = data.ts;
			this.dt = new Date(data.ts*1000).toISOString();

			this.chartIMUx.series[0].data.push(data.state.imu_x.toFixed(3));
			this.chartIMUy.series[0].data.push(data.state.imu_y.toFixed(3));
			this.chartIMUz.series[0].data.push(data.state.imu_z.toFixed(3));

			this.mqtt_status = this.$mqtt.status();
		}
	},
	mounted() {
		this.mqtt_status = this.$mqtt.status();

		// subscribe to ground station topic to get state updates
		this.$mqtt.subscribe("ops-sat-1/spacecraft", (message) => {
			let data = JSON.parse(message);
			//console.log(data);

			if (data)
				this.updateData(data);
		}, false);
	}
}
</script>
<template>

	<div id="toasts-container" class="toasts-container" style="z-index: 10;"></div>

	<!-- BEGIN page-header -->
	<h1 class="page-header">
		FD <small>Flight Dynamics</small>
		<span v-if="loading" class="spinner-border text-secondary" role="status"><span class="visually-hidden">Loading...</span></span> 
		<small class="float-end">
			<span class="badge rounded-0 bg-secondary">Last Update</span>
			<span class="badge rounded-0 bg-dark" style="margin-right: 10px;">{{ dt.replace('T', ' ').replace('Z','') }} UTC</span>
			<span class="badge rounded-0 bg-secondary">MQTT</span>
			<span class="badge rounded-0" :class="{ 'bg-success': mqtt_status === 'connected', 'bg-danger': mqtt_status !== 'connected' }">{{ mqtt_status }}</span>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->


	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2">
			TODO
		</div>
	</div>

</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
</style>