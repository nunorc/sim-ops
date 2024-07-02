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
			config: null,
			state: null,
			status_dl: null,
			ts: -1,
			dt: '_',
			chartRotX: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rotation x', data: [] }]
			},
			chartRotY: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rotation y', data: [] }]
			},
			chartRotZ: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rotation z', data: [] }]
			},
			chartRateX: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rate x', data: [] }]
			},
			chartRateY: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rate y', data: [] }]
			},
			chartRateZ: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'rate z', data: [] }]
			},
			chartSunAngle: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'sun angle', data: [] }]
			},
			chartNadirAngle: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'nadir angle', data: [] }]
			},
			mqtt_status: "checking"
		}
	},
	methods: {
		updateData(data) {
			this.loading = false;
			this.state = data;
			this.ts = this.state.ts;
			this.dt = new Date(this.ts*1000).toISOString();

			this.chartRotX.series[0].data.push(this.state.aocs_rotation[0].toFixed(1));
			this.chartRotY.series[0].data.push(this.state.aocs_rotation[1].toFixed(1));
			this.chartRotZ.series[0].data.push(this.state.aocs_rotation[2].toFixed(1));
			this.chartRateX.series[0].data.push(this.state.aocs_rates[0].toFixed(1));
			this.chartRateY.series[0].data.push(this.state.aocs_rates[1].toFixed(1));
			this.chartRateZ.series[0].data.push(this.state.aocs_rates[2].toFixed(1));
			this.chartSunAngle.series[0].data.push(this.state.aocs_sun_angle.toFixed(1));
			this.chartNadirAngle.series[0].data.push(this.state.aocs_nadir_angle.toFixed(1));

			this.mqtt_status = this.$mqtt.status();
		}
	},
	mounted() {
		this.compact = JSON.parse(sessionStorage.getItem('compact')) || false;

		this.mqtt_status = this.$mqtt.status();

		// subscribe to spacecraft topic to get state updates
		this.$mqtt.subscribe("spacecraft", (message) => {
			try {
				let data = JSON.parse(message);
				console.log(data);

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
			catch (err) {
				console.log(err);
			}

		}, false);
	}
}
</script>
<template>

	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		AOCS <small class="d-none d-md-inline">Attitude and Orbit Control System</small>
		<small class="float-end">
			<span class="badge rounded-0 bg-secondary">MQTT</span>
			<span class="badge rounded-0" :class="{ 'bg-success': mqtt_status === 'connected', 'bg-danger': mqtt_status !== 'connected' }">{{ mqtt_status }}</span>
			<span class="badge rounded-0 bg-secondary ms-1">D/L State</span>
			<span v-if="status_dl" class="badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': status_dl==='NO_RF', 'text-bg-warning': status_dl==='PLL_LOCK' || status_dl==='PSK_LOCK' || status_dl==='BIT_LOCK', 'text-bg-success': status_dl==='FRAME_LOCK' }">{{ status_dl }}</span>
			<span v-else class="badge rounded-0 bg-dark">_</span>
		</small>
	</h1>
	<hr class="mb-4">

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-sm-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">AOCS Chain</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_chain }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-sm-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">AOCS Mode</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_mode }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-sm-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">AOCS Valid</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.aocs_valid==='not_valid', 'text-bg-dark': state.aocs_valid==='unkown', 'text-bg-theme': state.aocs_valid==='valid' }">{{ state.aocs_valid }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rotation X</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rotation[0].toFixed(3) }}°</h3>
						<div class="mt-1">
							<apexchart :height="chartRotX.height" :options="chartRotX.options" :series="chartRotX.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rotation Y</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rotation[1].toFixed(3) }}°</h3>
						<div class="mt-1">
							<apexchart :height="chartRotY.height" :options="chartRotY.options" :series="chartRotY.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rotation Z</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rotation[2].toFixed(3) }}°</h3>
						<div class="mt-1">
							<apexchart :height="chartRotZ.height" :options="chartRotZ.options" :series="chartRotZ.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rate X</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rates[0].toFixed(3) }} <small class="text-secondary app-fs-small">°/s</small></h3>
						<div class="mt-1">
							<apexchart :height="chartRateX.height" :options="chartRateX.options" :series="chartRateX.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rate Y</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rates[1].toFixed(3) }} <small class="text-secondary app-fs-small">°/s</small></h3>
						<div class="mt-1">
							<apexchart :height="chartRateY.height" :options="chartRateY.options" :series="chartRateY.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Rate Z</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_rates[2].toFixed(3) }} <small class="text-secondary app-fs-small">°/s</small></h3>
						<div class="mt-1">
							<apexchart :height="chartRateZ.height" :options="chartRateZ.options" :series="chartRateZ.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Sun Angle</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_sun_angle.toFixed(3) }}°</h3>
						<div class="mt-1">
							<apexchart :height="chartSunAngle.height" :options="chartSunAngle.options" :series="chartSunAngle.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Nadir Angle</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.aocs_nadir_angle.toFixed(3) }}°</h3>
						<div class="mt-1">
							<apexchart :height="chartNadirAngle.height" :options="chartNadirAngle.options" :series="chartNadirAngle.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && compact">
		<div class="col-sm-4">
			<card class="mb-3">
				<card-body class="">
					<table class="table text-nowrap mb-0">
						<tbody>
							<tr>
								<td class="app-w-col">AOCS Chain</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_chain }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>AOCS Mode</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_mode }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>AOCS Valid</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_valid }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rotation X</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rotation[0].toFixed(3) }}°</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rotation Y</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rotation[1].toFixed(3) }}°</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rotation Z</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rotation[2].toFixed(3) }}°</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rate X</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rates[0].toFixed(3) }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rate Y</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rates[1].toFixed(3) }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Rate Z</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_rates[2].toFixed(3) }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Sun Angle</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_sun_angle.toFixed(3) }}°</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Nadir Angle</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.aocs_nadir_angle.toFixed(3) }}°</div></td>
								<td v-else>_</td>
							</tr>
						</tbody>
					</table>
				</card-body>
			</card>
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
.app-w-col { width: 70%; }
.app-badge { font-size: 0.7rem; font-weight: 600; text-align: center; padding: 2px; }
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
</style>