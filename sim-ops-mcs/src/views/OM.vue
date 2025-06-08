<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import apexchart from '@/components/plugins/Apexcharts.vue';
import chartjs from '@/components/plugins/Chartjs.vue';
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
			ts: -1,
			dt: '_',
			chartElevation: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Elevation', data: [] }]
			},
			chartAzimuth: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Azimuth', data: [] }]
			},
			chartDistance: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false } },
				series: [{ name: 'Distance', data: [] }]
			},
			chartSnr: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false }, yaxis: { } },
				series: [{ name: 'SNR', data: [] }]
			},
			chartVelocity: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false }, yaxis: { } },
				series: [{ name: 'Velocity', data: [] }]
			},
			chartTX: {
				height: 100,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false,  }, yaxis: { min: -20, max: 60 },
					annotations: {
						yaxis: [{ y: 45, borderColor: '#ff0000' }]  }}, // yaxis: { min: 20, max: 55 }
				series: [{ name: 'Power', data: [] }]
			},
			chartRX: {
				height: 100,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false }, yaxis: { min: -130, max: -90 },
				annotations: {
						yaxis: [{ y: -109, borderColor: '#ff0000' }]  }},
				series: [{ name: 'Power', data: [] }]
			},
			controlLog: [],
			control_send: '',
			control_recv: '',
			control_recv_loading: false,
			mqtt_status: "checking"
		}
	},
	methods: {
		updateData(data) {
			this.loading = false;

			// trigger sweep
			if (data.sweep_count > 0 && this.state && data.sweep_count > this.state.sweep_count) {

				const s1 = document.getElementById('sweep-1');

				s1.classList.add('sweep-bar-anim');
				setTimeout(() => { s1.classList.remove('sweep-bar-anim')}, 10000)
			}

			this.state = data;
			this.ts = data.ts;
			this.dt = new Date(data.ts*1000).toISOString();

			if (this.state.elevation > 0) {
				this.chartElevation.series[0].data.push(this.state.elevation.toFixed(2));
				this.chartAzimuth.series[0].data.push(this.state.azimuth.toFixed(2));
			}

			if (this.state.auto_range) {
				this.chartDistance.series[0].data.push(this.state.distance.toFixed(0));
			}
			else {
				this.chartDistance.series[0].data = [];
			}

			if (this.state.snr_dl > -128) {
				this.chartSnr.series[0].data.push(this.state.snr_dl.toFixed(2));
			}
			else {
				this.chartSnr.series[0].data = [];
			}

			if (this.state.doppler_enabled) {
				this.chartVelocity.series[0].data.push(this.state.doppler_velocity.toFixed(2));
			}
			else {
				this.chartVelocity.series[0].data = [];
			}

			this.chartTX.series[0].data = this.state.spectrum_ul;
			this.chartRX.series[0].data = this.state.spectrum_dl;

			this.mqtt_status = this.$mqtt.status();
		},
		sendCommand(command, value, event) {
			let button = event.target;

			button.disabled = true;
			this.control_send = `${command} ${value}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			let body = { 'system': 'ground_station',  'control': command, 'value': value };
			axios.post(`${appOption.soAPI}/control`, body)
				.then((resp) => {
					this.control_recv = resp.data.status;
					button.disabled = false;
					this.control_recv_loading = false;
				})
		},
		diffDatesStr(later) {
			if (later < this.state.ts)
				return '_';

			let delta = Math.abs(later - this.state.ts);

			let days = Math.floor(delta/86400);
			delta -= days * 864001;

			let hours = Math.floor(delta/3600) % 24;
			delta -= hours * 3600;

			let minutes = Math.floor(delta/60) % 60;
			delta -= minutes * 60;

			let seconds = Math.floor(delta % 60);

			let res = 'in ';
			if (days > 0)
				res += days+'d '
			if (hours > 0)
				res += hours+'h '
			if (minutes > 0)
				res += minutes+'m '
			if (seconds >= 0)
				res += seconds+'s '

			return res;
		}
	},
	mounted() {
		this.mqtt_status = this.$mqtt.status();

		// subscribe to ground station topic to get state updates
		this.$mqtt.subscribe("ground_station", (message) => {
			try {
				let data = JSON.parse(message);

				if (data) {
					const dt = new Date(data.ts*1000).toISOString();
					document.getElementById("dt-now").innerHTML = dt.replace('T', ' ').replace('Z','') + ' UTC';
					this.updateData(data);
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
		OM <small>Ground Operations Manager</small>
		<small class="float-end">
			<span class="badge rounded-0 bg-secondary">MQTT</span>
			<span class="badge rounded-0" :class="{ 'bg-success': mqtt_status === 'connected', 'bg-danger': mqtt_status !== 'connected' }">{{ mqtt_status }}</span>
		</small>
	</h1>
	<hr class="mb-4">

	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">D/L Status</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.status_dl==='NO_RF', 'text-bg-warning': state.status_dl==='PLL_LOCK' || state.status_dl==='PSK_LOCK' || state.status_dl==='BIT_LOCK', 'text-bg-success': state.status_dl==='FRAME_LOCK' }">{{ state.status_dl }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Frame Quality</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-theme': state.frame_quality==='good', 'text-bg-danger': state.frame_quality==='bad', 'text-bg-warning': state.frame_quality==='unknown' }">{{ state.frame_quality }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Frame Checks</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-theme': state.frame_checks==='enabled', 'text-bg-danger': state.frame_checks!=='enabled' }">{{ state.frame_checks }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Program Track</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': !state.program_track, 'text-bg-theme': state.program_track }">{{ state.program_track ? 'Enabled' : 'Disabled' }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Ground Station</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">{{ state.name }}</span>
						<span v-else>_</span>
					</h5>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Next AOS</card-header>
				<card-body class="p-2 mx-2">
					<p class="mb-0 text-center">
						<span v-if="state">{{ diffDatesStr(state.next_pass_start) }}</span>
						<span v-else>_</span>
					</p>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L Carrier</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': state.carrier_ul !== 'on', 'text-bg-success': state.carrier_ul === 'on' }">{{ state.carrier_ul === 'on' ? 'enabled' : 'disabled' }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Sweep Done</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': !state.sweep_done, 'text-bg-success': state.sweep_done }">{{ state.sweep_done }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L Power</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">{{ state.power_ul }} <small class="text-secondary app-fs-small"> dBm</small></span>
						<span v-else>_</span>
					</h5>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L &#183; D/L Bands</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">S &#183; {{ state.mode.charAt(0) }}</span>
						<span v-else>_</span>
					</h5>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Mode</card-header>
				<card-body class="p-2 mx-2">
					<h5 class="mb-0 text-center">
						<span v-if="state">{{ state.mode }}</span>
						<span v-else>_</span>
					</h5>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Next LOS</card-header>
				<card-body class="p-2 mx-2">
					<p class="mb-0 text-center">
						<span v-if="state">{{ diffDatesStr(state.next_pass_end) }}</span>
						<span v-else>_</span>
					</p>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2 offset-xl-4 offset-lg-4">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Ranging</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': !state.auto_range, 'text-bg-theme': state.auto_range }">{{ state.auto_range ? 'Enabled' : 'Disabled' }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Doppler</card-header>
				<card-body class="p-2 mx-2">
					<span v-if="state" class="badge rounded-0 app-w-100 text-uppercase" :class="{ 'text-bg-danger': !state.doppler_enabled, 'text-bg-theme': state.doppler_enabled }">{{ state.doppler_enabled ? 'Enabled' : 'Disabled' }}</span>
					<span v-else>_</span>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Elevation</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.elevation > 0 ? state.elevation.toFixed(2)+'°' : '_' }}</h3>
						<div class="mt-1">
							<apexchart :height="chartElevation.height" :options="chartElevation.options" :series="chartElevation.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Azimuth</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.azimuth > 0 ? state.azimuth.toFixed(2)+'°' : '_' }}</h3>
						<div class="mt-1">
							<apexchart :height="chartAzimuth.height" :options="chartAzimuth.options" :series="chartAzimuth.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Range</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.distance > 0 && state.auto_range ? state.distance.toFixed(0) : '_' }} <small v-if="state.distance > 0 && state.auto_range" class="text-secondary app-fs-small"> km</small></h3>
						<div class="mt-1">
							<apexchart :height="chartDistance.height" :options="chartDistance.options" :series="chartDistance.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Velocity</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.doppler_enabled ? state.doppler_velocity.toFixed(2) : '_' }} <small v-if="state.doppler_enabled" class="text-secondary app-fs-small"> km/s</small></h3>
						<div class="mt-1">
							<apexchart :height="chartVelocity.height" :options="chartVelocity.options" :series="chartVelocity.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">D/L SNR</card-header>
				<card-body>
					<div class="row align-items-center" v-if="state">
						<h3 class="mb-0 text-center">{{ state.snr_dl > -128 ? state.snr_dl.toFixed(3) : '_' }} <small v-if="state.snr_dl > -128" class="text-secondary app-fs-small"> dB</small></h3>
						<div class="mt-1">
							<apexchart :height="chartSnr.height" :options="chartSnr.options" :series="chartSnr.series"></apexchart>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-6 col-lg-6">
			<card class="">
				<card-header class="card-header fw-bold small text-center p-1">U/L Spectrum</card-header>
				<card-body class="px-0 p-2 mx-3">
					<div id="sweep-1" class="sweep-bar"></div>
					<apexchart :height="chartTX.height" :options="chartTX.options" :series="chartTX.series"></apexchart>
				</card-body>
			</card>
		</div>
		<div class="col-xl-6 col-lg-6">
			<card class="">
				<card-header class="card-header fw-bold small text-center p-1">D/L Spectrum</card-header>
				<card-body class="px-0 p-2 mx-3">
					<apexchart :height="chartRX.height" :options="chartRX.options" :series="chartRX.series"></apexchart>
				</card-body>
			</card>
		</div>
	</div>

	<hr/>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Control</card-header>
				<card-body class="text-center" v-if="state">
					<button v-if="state.carrier_ul === 'off'" @click="sendCommand('carrier_ul', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Enable U/L Carrier</button>
					<button v-if="state.carrier_ul === 'on'" @click="sendCommand('carrier_ul', 'off', $event)" type="button" class="btn btn-sm btn-outline-danger app-w-80">Disable U/L Carrier</button>
					<span>&nbsp;</span>
					<button v-if="!state.program_track" @click="sendCommand('program_track', true, $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Enable Prog. Track</button>
					<button v-if="state.program_track" @click="sendCommand('program_track', false, $event)" type="button" class="btn btn-sm btn-outline-danger app-w-80">Disable Prog. Track</button>
					<span>&nbsp;</span>
					<button v-if="!state.auto_range" @click="sendCommand('auto_range', true, $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Enable Ranging</button>
					<button v-if="state.auto_range" @click="sendCommand('auto_range', false, $event)" type="button" class="btn btn-sm btn-outline-danger app-w-80">Disable Ranging</button>
					<span>&nbsp;</span>
					<button v-if="!state.doppler_enabled" @click="sendCommand('doppler_enabled', true, $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Enable Doppler</button>
					<button v-if="state.doppler_enabled" @click="sendCommand('doppler_enabled', false, $event)" type="button" class="btn btn-sm btn-outline-danger app-w-80">Disable Doppler</button>
					<span>&nbsp;</span>
					<button @click="sendCommand('sweep', true, $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Sweep</button>
					<span>&nbsp;</span>
					<button v-if="state.frame_checks === 'disabled'" @click="sendCommand('frame_checks', 'enabled', $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80">Enable Fr. Checks</button>
					<button v-if="state.frame_checks === 'enabled'" @click="sendCommand('frame_checks', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-danger app-w-80">Disable Fr. Checks</button>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">U/L Power</card-header>
				<card-body class="my-2">
					<select v-if="state" class="form-select form-select-lg" @change="sendCommand('power_ul', state.power_ul, $event)" v-model="state.power_ul">
						<option value="50">50</option>
						<option value="40">40</option>
						<option value="30">30</option>
					</select>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Configuration</card-header>
				<card-body class="my-2">
					<select v-if="state" class="form-select form-select-lg" @change="sendCommand('mode', state.mode, $event)" v-model="state.mode">
						<option v-for="m in state.modes" >{{ m }}</option>
					</select>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="pb-3">
				<card-header class="card-header fw-bold small text-center p-1">Control Console</card-header>
				<card-body class="p-2 mb-1">
					<table class="table table-sm table-striped table-borderless mb-2px small text-nowrap">
						<tbody>
							<tr><td><span>[S]&nbsp;</span><span style="font-size: smaller;">{{ control_send }}</span></td></tr>
							<tr><td><span>[R]&nbsp;</span>
								<span v-if="control_recv_loading" class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Loading...</span></span>
								<span class="fw-bold" :class="{ 'text-theme': control_recv==='OK', 'text-danger': control_recv!=='OK'}">{{ control_recv }}</span></td></tr>
						</tbody>
					</table>
				</card-body>
			</card>
		</div>
	</div>

</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
.sweep-bar {
	position: absolute;
    top: 0;
    left: 0;
    margin: 0;
    padding: 0;
    width: 17%;
    height: 100%;
    z-index: 10;
    opacity: 0;
    border-right: 2px solid rgb(60 210 165);
    background-image: linear-gradient(to right, rgba(60, 210, 165, 0), rgba(60, 210, 165,1));
}
.sweep-bar-anim {
	animation-name: fadeInAnimation;
	animation-duration: 5s;
	animation-timing-function: linear;
    animation-iteration-count: 1;
}
@keyframes fadeInAnimation {
    0% { opacity: 1; }
	10% { opacity: 1; }
	90% { opacity: 1; }
    100% { opacity: 1; left: 86%; }
}
</style>