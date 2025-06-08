<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import apexchart from '@/components/plugins/Apexcharts.vue';
import chartjs from '@/components/plugins/Chartjs.vue';

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
			chartBattery: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Battery', data: [] }]
			},
			chartPower: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Power', data: [] }]
			},
			chartTemperature: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Temperature', data: [] }]
			},
			mqtt_status: "checking",
			compact: false
		}
	},
	methods: {
		updateData(data) {
			this.loading = false;
			this.state = data;
			this.ts = this.state.ts;
			this.dt = new Date(this.state.ts*1000).toISOString();

			this.chartBattery.series[0].data.push(this.state.eps_battery_dod.toFixed(2));
			this.chartPower.series[0].data.push(this.state.eps_net_power.toFixed(2));
			this.chartTemperature.series[0].data.push(this.state.eps_temperature.toFixed(2));

			this.mqtt_status = this.$mqtt.status();
		}
	},
	mounted() {
		this.compact = JSON.parse(sessionStorage.getItem('compact')) || false;

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

					if (data.ov_no_tm !== true && data.status_dl === 'FRAME_LOCK' && data.ttc_obc === 'nominal') {
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

	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		EPS <small class="d-none d-md-inline">Electrical Power System</small>
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
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">EPS Chain</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.eps_chain }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Solar Array 1</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_sol_array[0] === 'nominal', 'bg-danger': state.eps_sol_array[0] !== 'nominal' }">{{ state.eps_sol_array[0] }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Solar Array 2</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_sol_array[1] === 'nominal', 'bg-danger': state.eps_sol_array[1] !== 'nominal' }">{{ state.eps_sol_array[1] }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Battery DOD</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.eps_battery_dod.toFixed(2) }}%</h3>
						<div class="mt-1">
							<apexchart :height="chartBattery.height" :options="chartBattery.options" :series="chartBattery.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Net Power</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.eps_net_power.toFixed(2) }}</h3>
						<div class="mt-1">
							<apexchart :height="chartPower.height" :options="chartPower.options" :series="chartPower.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Temperature</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.eps_temperature.toFixed(2) }}°C</h3>
						<div class="mt-1">
							<apexchart :height="chartTemperature.height" :options="chartTemperature.options" :series="chartTemperature.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">ACU</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_acu === 'nominal', 'bg-danger': state.eps_acu !== 'nominal' }">{{ state.eps_acu }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">PDU</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_pdu === 'nominal', 'bg-danger': state.eps_pdu !== 'nominal' }">{{ state.eps_pdu }}</span>
					<span v-else>_</span>
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
								<td class="app-w-col">EPS Chain</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.eps_chain }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Solar Array 1</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_sol_array[0] === 'nominal', 'bg-danger': state.eps_sol_array[0] !== 'nominal' }">{{ state.eps_sol_array[0] }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Solar Array 2</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.eps_sol_array[1] === 'nominal', 'bg-danger': state.eps_sol_array[1] !== 'nominal' }">{{ state.eps_sol_array[1] }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Battery DOD</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.eps_battery_dod.toFixed(2) }}%</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Net Power</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.eps_net_power.toFixed(2) }}%</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Temperature</td>
								<td v-if="state"><div class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.eps_temperature.toFixed(2) }}%</div></td>
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