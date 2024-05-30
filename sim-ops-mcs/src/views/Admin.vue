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
			renderComponent: false,
			loading: true,
			running: null,
			name: '',
			scenarios: [],
			data: null,
			ov_control: 'max_status_dl',
			ov_value: '',
			admin_pw: '',
			overrides: [
				{ name: "Max D/L Status", value: 'max_status_dl' },
				{ name: "Max D/L SNR", value: 'max_snr_dl' },
				{ name: "On-board TX Transmitter", value: 'tx_status' },
				{ name: "Ground station U/L Carrier", value: 'carrier_ul' },
				{ name: "No TM", value: 'no_tm' },
				{ name: "No TC", value: 'no_tc' },
				{ name: "No Uploads", value: 'no_uploads' }
			],
			options: {
				'max_status_dl': ["NO_RF", "PLL_LOCK", "PSK_LOCK", "BIT_LOCK", "FRAME_LOCK"],
				'max_snr_dl': [],
				'tx_status': ["on", "off"],
				'carrier_ul': ["on", "off"],
				'no_tm': ['enabled'],
				'no_tc': ['enabled'],
				'no_uploads': ['enabled']
			},
			current: [],
			ts: -1,
			dt: '_',
			chartSnr: {
				height: 30,
				options: { chart: { type: 'line', sparkline: { enabled: true } }, colors: [appVariable.color.theme], stroke: { curve: 'straight', width: 2 }, tooltip: { enabled: false }, yaxis: { } },
				series: [{ name: 'SNR', data: [] }]
			},
			control_send: '',
			control_recv: '',
			control_recv_loading: false,
			mqtt_status: "checking"
		}
	},
	methods: {
		handleAuth() {
			this.admin_pw = document.getElementById("password").value;
			this.adminStatus();
		},
		resetAuth() {
			document.getElementById("auth-result").innerHTML = "";
		},
		adminStatus() {
			axios.get(`${appOption.soAPI}/admin/status?${new URLSearchParams({admin_pw:this.admin_pw})}`)
				.then((resp) => {
					if (resp.status===200) {
						this.loading = false;
						this.running = resp.data.running;
						this.scenarios = resp.data.scenarios;
						this.data = resp.data.data;
						this.name = resp.data.running ? resp.data.name : resp.data.scenarios[0];

						// overrides
						this.current = resp.data.overrides;

						this.renderComponent = true;
					}
					else {
						this.renderComponent = false;
					}
				})
		},
		adminRun(control, value, event) {
			let button = event.target;

			button.disabled = true;
			this.control_send = `${control} ${value}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			let body = { 'system': 'admin', 'control': control, 'value': value };
			axios.post(`${appOption.soAPI}/admin?${new URLSearchParams({admin_pw:this.admin_pw})}`, body)
				.then((resp) => {
					if (resp.status===200) {
						this.control_recv = resp.data.status;
						button.disabled = false;
						this.control_recv_loading = false;

						this.adminStatus();
					}
					else {
						this.renderComponent = false;
					}
				})
		},
		sendCommand(command, control, value, event) {
			let button = event.target;

			button.disabled = true;
			this.control_send = `${control} ${value}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			let body = { 'system': 'spacecraft',  'control': control, 'value': value, 'command': null };
			axios.post(`${appOption.soAPI}/control?${new URLSearchParams({admin_pw:this.admin_pw})}`, body)
				.then((resp) => {
					if (resp.status===200) {
						this.control_recv = resp.data.status;
						button.disabled = false;
						this.control_recv_loading = false;
					}
					else {
						this.renderComponent = false;
					}
				})
		},
		adminSet(control, value, event) {
			let button = event.target;

			button.disabled = true;
			this.control_send = `${control} ${value}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			let body = { 'system': 'override', 'control': control, 'value': value };
			axios.post(`${appOption.soAPI}/admin?${new URLSearchParams({admin_pw:this.admin_pw})}`, body)
				.then((resp) => {
					if (resp.status===200) {
						this.control_recv = resp.data.status;
						button.disabled = false;
						this.control_recv_loading = false;

						this.adminStatus();
					}
					else {
						this.renderComponent = false;
					}
				})
		}
	}
}
</script>
<template>

	<div id="toasts-container" class="toasts-container" style="z-index: 10;"></div>

	<!-- BEGIN page-header -->
	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		Admin
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<div class="row" v-if="!renderComponent">
		<div class="col">
			Password: <input type="password" id="password" class="mx-2" @input="resetAuth" @keydown.enter="handleAuth"/>
			<button class="btn btn-sm btn-outline-theme mx-2" @click="handleAuth">Login</button>
			<span id="auth-result" class="mx-2"></span>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Scenario</card-header>
				<card-body class="p-2 mx-2">
					<div class="row">
						<div class="col form-group">
							<label class="form-label">Status</label><br/>
							<span v-if="!loading" class="badge rounded-0 text-uppercase" :class="{ 'text-bg-success': running, 'text-bg-danger': !running }">{{ running ? 'Running' : 'Not running' }}</span>
						</div>
						<div class="col form-group">
							<label class="form-label">Name</label>
							<select class="form-select form-control" v-model="name">
								<option v-for="s in scenarios">{{ s }}</option>
							</select>
						</div>
						<div class="col-sm-4 d-flex justify-content-center align-items-center">
							<button v-if="!running" @click="adminRun('start', name, $event)" type="button" class="btn btn-outline-theme">Start</button>
							<button v-if="running" @click="adminRun('stop', name, $event)" type="button" class="btn btn-outline-danger" style="margin-left: 10px;">Stop</button>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Admin Console</card-header>
				<card-body class="p-3">
					<table class="table table-sm table-striped table-borderless mb-0 small text-nowrap">
						<tbody>
							<tr><td><span>&nbsp;[Send]&nbsp;</span><span>{{ control_send }}</span></td></tr>
							<tr><td><span>&nbsp;[Recv]&nbsp;</span>
								<span v-if="control_recv_loading" class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Loading...</span></span>
								<span class="fw-bold" :class="{ 'text-theme': control_recv==='OK', 'text-danger': control_recv!=='OK'}">{{ control_recv }}</span></td></tr>
						</tbody>
					</table>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Add Override</card-header>
				<card-body class="p-2 mx-2">
					<div class="row">
						<div class="col-6 form-group">
							<label class="form-label">Control</label>
							<select class="form-control form-select" v-model="ov_control">
								<option v-for="ov in overrides" :value="ov.value">{{ ov.name }}</option>
							</select>
						</div>
						<div class="col-3 form-group">
							<label class="form-label">Value</label>
							<select v-if="options[ov_control].length > 0" class="form-control form-select" v-model="ov_value" :disabled="!running">
								<option v-for="opt in options[ov_control]" :value="opt">{{ opt }}</option>
							</select>
							<input v-if="options[ov_control].length === 0" type="text" class="form-control" v-model="ov_value" placeholder="">
						</div>
						<div class="col-3 d-flex justify-content-center align-items-center">
							<button @click="adminSet(ov_control, ov_value, $event)" type="button" class="btn btn-outline-theme">Set</button>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Current Overrides</card-header>
				<card-body class="p-3 mb-1">
					<span v-if="current.length === 0">None</span>
					<table v-if="current.length > 0" class="table table-sm table-striped table-borderless mb-2px small text-nowrap">
						<thead>
							<tr><td>Control</td><td>Value</td><td></td></tr>
						</thead>
						<tbody>
							<tr v-for="c in current">
								<td>{{ c[0] }}</td>
								<td>{{ c[1] }}</td>
								<td><button @click="adminSet('_unset', c[0], $event)" type="button" class="btn btn-sm btn-outline-danger">Unset</button></td>
							</tr>
						</tbody>
					</table>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row" v-if="renderComponent">
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Actions</card-header>
				<card-body class="text-center">
					<button @click="sendCommand(null, 'safe_mode', true, $event)" type="button" class="btn btn-sm btn-outline-theme app-w-80" :disabled="!running">Trigger Safe Mode</button>
				</card-body>
			</card>
		</div>
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">Scenario Details</card-header>
				<card-body>
					<table class="table table-sm table-borderless mb-2px small">
						<tbody v-if="data">
							<!-- <tr v-if="state && state.tc_history.length === 0">
								<td>None</td>
							</tr> -->
							<tr v-for="(v, k) in data[name]">
								<td>{{ k }}</td><td><code>{{ v }}</code></td>
							</tr>
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
</style>
