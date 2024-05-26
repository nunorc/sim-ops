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
			loading: true,
			state: null,
			status_dl: null,
			ts: -1,
			dt: '_',
            chartBattery: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Battery', data: [] }]
			},
			chartTemperature: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Temperature', data: [] }]
			},
            chartMemory: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Memory', data: [] }]
			},
			mqtt_status: "checking"
		}
	},
	methods: {
		updateData(data) {
			this.loading = false;
			this.state = data;
			this.ts = this.state.ts;
			this.dt = new Date(this.state.ts*1000).toISOString();

			this.chartBattery.series[0].data.push(this.state.pts_battery_dod.toFixed(2));
			this.chartTemperature.series[0].data.push(this.state.pts_temperature.toFixed(2));
            this.chartMemory.series[0].data.push(this.state.dhs_memory.toFixed(2));

			this.mqtt_status = this.$mqtt.status();
		}
	},
	mounted() {
		this.mqtt_status = this.$mqtt.status();

		// subscribe to ground station topic to get state updates
		this.$mqtt.subscribe("spacecraft", (message) => {
			try {
				let data = JSON.parse(message);

				if (data) {
					this.status_dl = data.status_dl;
					const dt = new Date(data.ts*1000).toISOString(),
						dt_str = dt.replace('T', ' ').replace('Z','') + ' UTC';
					document.getElementById("dt-now").innerHTML = dt_str;

					if (data.status_dl === 'FRAME_LOCK') {
						this.updateData(data);
						const el = document.getElementById("dt-last-up");
						if (el)
							el.innerHTML = dt_str;
					}
				}
			}
			catch(err){
				console.log(err);
			}
		}, false);
	}
}
</script>
<template>

	<!-- BEGIN page-header -->
	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		Spacecraft <small>Monitor</small>
		<small class="float-end">
			<!-- <span class="badge rounded-0 bg-secondary">Last Update</span>
			<span class="badge rounded-0 bg-dark" style="margin-right: 10px;">{{ dt.replace('T', ' ').replace('Z','') }} UTC</span> -->
			<span class="badge rounded-0 bg-secondary">MQTT</span>
			<span class="badge rounded-0" :class="{ 'bg-success': mqtt_status === 'connected', 'bg-danger': mqtt_status !== 'connected' }">{{ mqtt_status }}</span>
			<span class="badge rounded-0 bg-secondary ms-2">D/L State</span>
			<span v-if="status_dl" class="badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': status_dl==='NO_RF', 'text-bg-warning': status_dl==='PLL_LOCK' || status_dl==='PSK_LOCK' || status_dl==='BIT_LOCK', 'text-bg-success': status_dl==='FRAME_LOCK' }">{{ status_dl }}</span>
			<span v-else class="badge rounded-0 bg-dark">_</span>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<div class="row">
		<div class="col">
			<h4>AOCS</h4>
			<div class="row" v-if="renderComponent">
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">AOCS Chain</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_chain }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">AOCS Mode</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_mode }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">AOCS valid</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_valid }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
			</div>
		</div>
		<div class="col">
			<h4>TTC</h4>
			<div class="row" v-if="renderComponent">
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">TTC Chain</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.ttc_chain }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">U/L Status</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.ttc_state_ul==='NO_RF', 'text-bg-warning': state.ttc_state_ul==='PLL_LOCK' || state.ttc_state_ul==='PSK_LOCK' || state.ttc_state_ul==='BIT_LOCK', 'text-bg-success': state.ttc_state_ul==='FRAME_LOCK' }">{{ state.ttc_state_ul }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">TTC Mode</card-header>
						<card-body class="p-2 mx-2">
							<h5 class="mb-0 text-center">
								<span v-if="state">{{ state.ttc_mode }}</span>
								<span v-else>_</span>
							</h5>
						</card-body>
					</card>
				</div>
			</div>
		</div>
	</div>

	<div class="row">
		<div class="col">
			<h4>PTS</h4>
			<div class="row" v-if="renderComponent">
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">PTS Chain</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_chain }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">Battery DOD</card-header>
						<card-body>
							<div class="row align-items-center" v-if="state">
								<h3 class="mb-0 text-center">{{ state.pts_battery_dod.toFixed(2) }}%</h3>
								<div class="mt-1">
									<apexchart :height="chartBattery.height" :options="chartBattery.options" :series="chartBattery.series"></apexchart>
								</div>
							</div>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">Temperature</card-header>
						<card-body>
							<div class="row align-items-center" v-if="state">
								<h3 class="mb-0 text-center">{{ state.pts_temperature.toFixed(2) }}°C</h3>
								<div class="mt-1">
									<apexchart :height="chartTemperature.height" :options="chartTemperature.options" :series="chartTemperature.series"></apexchart>
								</div>
							</div>
						</card-body>
					</card>
				</div>
			</div>
		</div>
		<div class="col">
			<h4>DHS</h4>
			<div class="row" v-if="renderComponent">
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">DHS Chain</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.dhs_chain }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">OBSW Mode</card-header>
							<card-body class="p-2 mx-2">
								<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-theme': state.dhs_obsw_mode === 'nominal', 'bg-danger': state.dhs_obsw_mode !== 'nominal'}">{{ state.dhs_obsw_mode }}</span>
								<span v-else>_</span>
							</card-body>
					</card>
				</div>
				<div class="col-xl-4 col-lg-4">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">Memory Usage</card-header>
						<card-body>
							<div class="row align-items-center" v-if="state">
								<h3 class="mb-0 text-center">{{ state.dhs_memory.toFixed(2) }}%</h3>
								<div class="mt-1">
									<apexchart :height="chartMemory.height" :options="chartMemory.options" :series="chartMemory.series"></apexchart>
								</div>
							</div>
						</card-body>
					</card>
				</div>
			</div>
		</div>
	</div>

	<div class="row">
		<div class="col">
			<h4>Payload</h4>
			<div class="row" v-if="renderComponent">
				<div class="col-xl-2 col-lg-2">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">GPS Status</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-theme': state.pl_gps_status==='on', 'bg-danger': state.pl_gps_status!=='on' }">{{ state.pl_gps_status }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
				<div class="col-xl-2 col-lg-2">
					<card class="mb-3">
						<card-header class="card-header fw-bold small text-center p-1">Camera Status</card-header>
						<card-body class="p-2 mx-2">
							<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-theme': state.pl_camera_status==='on', 'bg-danger': state.pl_camera_status!=='on' }">{{ state.pl_camera_status }}</span>
							<span v-else>_</span>
						</card-body>
					</card>
				</div>
			</div>
		</div>
	</div>

	<div class="row mt-3" v-if="renderComponent">
		<div class="col">
			<span class="badge rounded-0 bg-secondary">Last Update</span>
			<span class="badge rounded-0 bg-dark" id="dt-last-up">_</span>
		</div>
	</div>

</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
</style>