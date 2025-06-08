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
			state: null,
			status_dl: null,
			ts: -1,
			dt: '_',
			chartSnr: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false }, yaxis: { } },
				series: [{ name: 'SNR', data: [] }]
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

			if (this.state.ttc_snr_ul && this.state.ttc_snr_ul > -4 && this.state.ttc_state_ul !== 'NO_RF') {
				this.chartSnr.series[0].data.push(this.state.ttc_snr_ul.toFixed(1));
			}

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

					if (data.ov_no_tm !== true && data.status_dl === 'FRAME_LOCK') {
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
		TTC <small class="d-none d-md-inline">Telemetry, Tracking & Command</small>
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
				<card-header class="card-header fw-bold small text-center p-1">TTC Chain</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase bg-dark">{{ state.ttc_chain }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L Status</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.ttc_state_ul==='NO_RF', 'text-bg-warning': state.ttc_state_ul==='PLL_LOCK', 'text-bg-success': state.ttc_state_ul==='BIT_LOCK' }">{{ state.ttc_state_ul }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">OBC Status</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-success': state.ttc_obc === 'nominal', 'bg-danger': state.ttc_obc !== 'nominal' }">{{ state.ttc_obc }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
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
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Ranging</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.ttc_ranging === 'disabled', 'text-bg-success': state.ttc_ranging === 'enabled' }">{{ state.ttc_ranging }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Coherent</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.ttc_coherent === 'disabled', 'text-bg-success': state.ttc_coherent === 'enabled' }">{{ state.ttc_coherent }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent && !compact">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L SNR</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.ttc_snr_ul && state.ttc_snr_ul > -4 && state.ttc_state_ul !== 'NO_RF' ? state.ttc_snr_ul.toFixed(1) : '_' }} <small v-if="state.ttc_snr_ul && state.ttc_snr_ul > -4 && state.ttc_state_ul !== 'NO_RF'" class="text-secondary app-fs-small"> dB</small></h3>
						<div class="mt-1">
							<apexchart :height="chartSnr.height" :options="chartSnr.options" :series="chartSnr.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TX Status</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-theme': state.ttc_tx_status === 'on', 'text-bg-danger': state.ttc_tx_status !== 'on' }">{{ state.ttc_tx_status }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Ping Ack</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'bg-dark': state.ttc_ping_ack===0, 'text-bg-success': state.ttc_ping_ack>0}">{{ state.ttc_ping_ack }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TTC Sb Antenna</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">{{ state.ttc_s_antenna }}</span>
						<span v-else>_</span>
					</h5>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TTC Xb Antenna</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">{{ state.ttc_x_antenna }}</span>
						<span v-else>_</span>
					</h5>
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
								<td class="app-w-col">TTC Chain</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.ttc_chain }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>TTC Mode</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.ttc_mode }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>U/L Status</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': state.ttc_state_ul==='NO_RF', 'text-bg-warning': state.ttc_state_ul==='PLL_LOCK', 'text-bg-success': state.ttc_state_ul==='BIT_LOCK' }">{{ state.ttc_state_ul }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>OBC Status</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'bg-success': state.ttc_obc === 'nominal', 'bg-danger': state.ttc_obc !== 'nominal' }">{{ state.ttc_obc }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>U/L SNR</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase bg-dark">{{ state.ttc_snr_ul && state.ttc_snr_ul > -4 && state.ttc_state_ul !== 'NO_RF' ? state.ttc_snr_ul.toFixed(1) : '_' }} <small style="text-transform: none;">dBm</small></div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>TX Status</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'text-bg-theme': state.ttc_tx_status === 'on', 'text-bg-danger': state.ttc_tx_status !== 'on' }">{{ state.ttc_tx_status }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Ranging</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': state.ttc_ranging === 'disabled', 'text-bg-success': state.ttc_ranging === 'enabled'}">{{ state.ttc_ranging }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Coherent</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': state.ttc_coherent === 'disabled', 'text-bg-success': state.ttc_coherent === 'enabled'}">{{ state.ttc_coherent }}</div></td>
								<td v-else>_</td>
							</tr>
							<tr>
								<td>Ping Ack</td>
								<td v-if="state"><div class="app-badge rounded-0 text-uppercase" :class="{ 'bg-dark': state.ttc_ping_ack===0, 'text-bg-success': state.ttc_ping_ack>0}">{{ state.ttc_ping_ack }}</div></td>
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