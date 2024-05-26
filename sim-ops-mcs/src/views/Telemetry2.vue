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
		Telemetry <small>Monitor</small>
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
		<div class="col-sm-4">
				<card class="mb-3">
          <card-header class="card-header fw-bold small text-center p-1">AOCS</card-header>
					<card-body class="">
						<table class="table table-sm text-nowrap mb-0">
							<tbody>
								<tr>
									<td class="app-w-col">AOCS Chain</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_chain }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>AOCS Mode</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_mode }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>AOCS Valid</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_valid }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rotation X</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rotation[0].toFixed(3) }}°</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rotation Y</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rotation[1].toFixed(3) }}°</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rotation Z</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rotation[2].toFixed(3) }}°</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rate X</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rates[0].toFixed(3) }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rate Y</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rates[1].toFixed(3) }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Rate Z</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_rates[2].toFixed(3) }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Sun Angle</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_sun_angle.toFixed(3) }}°</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Nadir Angle</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.aocs_nadir_angle.toFixed(3) }}°</td>
									<td v-else>_</td>
								</tr>
							</tbody>
						</table>
					</card-body>
				</card>
		</div>
		<div class="col-sm-4">
				<card class="mb-3">
          <card-header class="card-header fw-bold small text-center p-1">TTC</card-header>
					<card-body class="">
						<table class="table table-sm text-nowrap mb-0">
							<tbody>
								<tr>
									<td class="app-w-col">TTC Chain</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.ttc_chain }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>TTC Mode</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.ttc_mode }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>U/L Status</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.ttc_state_ul==='NO_RF', 'text-bg-warning': state.ttc_state_ul==='PLL_LOCK' || state.ttc_state_ul==='PSK_LOCK' || state.ttc_state_ul==='BIT_LOCK', 'text-bg-success': state.ttc_state_ul==='FRAME_LOCK' }">{{ state.ttc_state_ul }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>U/L SNR</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.ttc_snr_ul && state.ttc_snr_ul > -4 && state.ttc_state_ul !== 'NO_RF' ? state.ttc_snr_ul.toFixed(1) : '_' }} <small style="text-transform: none;">dBm</small></td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>TX Status</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-theme': state.ttc_tx_status === 'on', 'text-bg-danger': state.ttc_tx_status !== 'on' }">{{ state.ttc_tx_status }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Coherent</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-success': state.ttc_coherent, 'text-bg-danger': !state.ttc_coherent}">{{ state.ttc_coherent }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Ping Ack</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-dark': state.ttc_ping_ack===0, 'text-bg-success': state.ttc_ping_ack>0}">{{ state.ttc_ping_ack }}</td>
									<td v-else>_</td>
								</tr>
							</tbody>
						</table>
					</card-body>
				</card>
		</div>
		<div class="col-sm-4">
				<card class="mb-3">
          <card-header class="card-header fw-bold small text-center p-1">PTS</card-header>
					<card-body class="">
						<table class="table table-sm text-nowrap mb-0">
							<tbody>
								<tr>
									<td class="app-w-col">PTS Chain</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_chain }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Solar Array 1</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.pts_sol_array[0] === 'nominal', 'bg-danger': state.pts_sol_array[0] !== 'nominal' }">{{ state.pts_sol_array[0] }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Solar Array 2</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.pts_sol_array[1] === 'nominal', 'bg-danger': state.pts_sol_array[1] !== 'nominal' }">{{ state.pts_sol_array[1] }}</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Battery DOD</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_battery_dod.toFixed(2) }}%</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Net Power</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_net_power.toFixed(2) }}%</td>
									<td v-else>_</td>
								</tr>
								<tr>
									<td>Temperature</td>
									<td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_temperature.toFixed(2) }}%</td>
									<td v-else>_</td>
								</tr>
							</tbody>
						</table>
					</card-body>
				</card>
		</div>
		<div class="col-sm-4">
      <card class="mb-3">
        <card-header class="card-header fw-bold small text-center p-1">DHS</card-header>
        <card-body class="">
          <table class="table table-sm text-nowrap mb-0">
            <tbody>
              <tr>
                <td class="app-w-col">PTS Chain</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_chain }}</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Solar Array 1</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.pts_sol_array[0] === 'nominal', 'bg-danger': state.pts_sol_array[0] !== 'nominal' }">{{ state.pts_sol_array[0] }}</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Solar Array 2</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.pts_sol_array[1] === 'nominal', 'bg-danger': state.pts_sol_array[1] !== 'nominal' }">{{ state.pts_sol_array[1] }}</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Battery DOD</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_battery_dod.toFixed(2) }}%</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Net Power</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_net_power.toFixed(2) }}%</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Temperature</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pts_temperature.toFixed(2) }}%</td>
                <td v-else>_</td>
              </tr>
            </tbody>
          </table>
        </card-body>
      </card>
		</div>
		<div class="col-sm-4">
      <card class="mb-3">
        <card-header class="card-header fw-bold small text-center p-1">Payload</card-header>
        <card-body class="">
          <table class="table table-sm text-nowrap mb-0">
            <tbody>
              <tr>
                <td class="app-w-col">GPS Status</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-theme': state.pl_gps_status==='on', 'bg-danger': state.pl_gps_status!=='on' }">{{ state.pl_gps_status }}</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Latitude</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pl_gps_pos[0].toFixed(3) }}°</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Longitude</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pl_gps_pos[1].toFixed(3) }}°</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td>Altitude</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.pl_gps_pos[2].toFixed(3) }}°</td>
                <td v-else>_</td>
              </tr>
              <tr>
                <td class="app-w-col">Camera Status</td>
                <td v-if="state" class="app-badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-theme': state.pl_camera_status==='on', 'bg-danger': state.pl_camera_status!=='on' }">{{ state.pl_camera_status }}</td>
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
.app-badge { font-size: 0.75rem; font-weight: 600; text-align: center; vertical-align: bottom; }
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
</style>