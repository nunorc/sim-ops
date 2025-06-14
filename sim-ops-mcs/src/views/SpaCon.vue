<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import axios from 'axios';
import { Modal } from 'bootstrap';

const appVariable = useAppVariableStore(),
      appOption = useAppOptionStore();

export default {
	data() {
		return {
			renderComponent: true,
			loading: true,
			activityLog: [],
			controlLog: [],
			control_send: '',
			control_recv: '',
			control_recv_loading: false,
			file_upload: null,
			ul_state: 'NO_RF',
			mqtt_status: "checking",
			manual_stack: [ { 'command': 'none' }, { 'command': 'none' }, { 'command': 'none' } ],
			tc_history: [ ['none', ' '], ['none', ' '], ['none', ' '] ],
			is_armed: false,
			flight_dynamics: null
		}
	},
	methods: {
		addStack(command, control, value, event) {
			let body = { 'system': 'spacecraft',  'control': control, 'value': value, 'command': command };

			for (let i=0; i<3; i++) {
				if (this.manual_stack[i].command == 'none') {
					this.manual_stack[i] = body;
					break;
				}
			}
		},
		lenStack() {
			let c = 0;
			this.manual_stack.forEach((el) => {
				if (el.command != 'none')
					c = c + 1;
			});
			return c;
		},
		armButton() {
			this.is_armed = true;
			this.toggleArm();
		},
		toggleArm() {
			const b = document.getElementById("arm-button"),
				  r = document.getElementById("manual-stack").rows[0],
				  c = r.cells[0];

			c.classList.toggle("text-warning");
			c.classList.toggle("text-success");
			c.classList.toggle("app-tc-loaded");
			c.classList.toggle("app-tc-armed");
		},
		goButton() {
			let body = this.manual_stack[0];
			this.manual_stack[0] = this.manual_stack[1];
			this.manual_stack[1] = this.manual_stack[2];
			this.manual_stack[2] = { 'command': 'none' };

			this.toggleArm();
			this.updateHistory(body.command);
			this.sendCommand(body);
		},
		updateHistory(command) {
			this.tc_history[2] = this.tc_history[1];
			this.tc_history[1] = this.tc_history[0];
			this.tc_history[0] = [command, '_'];
		},
		sendCommand(body) {
			axios.post(`${appOption.soAPI}/control`, body)
				.then((resp) => {
					this.tc_history[0][1] = this.resCommand(resp.data.status);
					this.is_armed = false;
				})
		},
		resCommand(status) {
			let split_1 = status.split(' ');

			let parts = [];
			split_1.forEach((sp) => {
				let split_2 = sp.split(':');
				let class_ = 'text-theme';
				if (split_2[0]=='w')
					class_ = 'text-warning';
				if (split_2[0]=='r')
					class_ = 'text-danger';

				parts.push(`<span class='${class_}'>${split_2[1]}</span>`);
			})

			return parts.join('&nbsp;&nbsp;');
		},
		delCommand(i) {
			console.log('del command '+i);
			this.manual_stack = this.manual_stack.slice(0, i).concat(this.manual_stack.slice(i+1));
			this.manual_stack[2] = { 'command': 'none' };
			return false;
		},
		fileUpload(type, event) {
			let filename = this.file_upload
			if (type == 'fd-ttq')
				filename = document.querySelector('input[name="fd_ttq_select"]:checked').value;

			this.control_send = `upload ${type} ${filename}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			this.closeModal1();
			this.closeModal2();
			this.closeModal3();
			this.closeModal4();

			this.updateHistory(`DHS_Uplink ${type}`);
			let body = { 'system': 'spacecraft',  'control': 'dhs_uploaded', 'value': `${type} > ${filename}`, 'command': `uploaded: ${type} > ${filename}` };
			axios.post(`${appOption.soAPI}/control`, body)
				.then((resp) => {
					this.tc_history[0][1] = this.resCommand(resp.data.status);
				})
		},
		onFileChange(event) {
			const files = event.target.files;

			if (files) {
				this.file_upload = files[0].name;
			}
		},
		openModal1() {
			this.my_modal_1.show();
		},
		openModal2() {
			this.my_modal_2.show();
		},
		openModal3() {
			this.my_modal_3.show();
		},
		openModal4() {
			axios.get(`${appOption.soAPI}/obj-store/fd`)
				.then(response => {
					this.flight_dynamics = response.data.filter(e => e.status > 0);
				})
				.catch(error => {
					console.log(this.error);
				})
				.finally(() => {
					this.my_modal_4.show();
				});
		},
		closeModal1() {
			this.my_modal_1.hide();
		},
		closeModal2() {
			this.my_modal_2.hide();
		},
		closeModal3() {
			this.my_modal_3.hide();
		},
		closeModal4() {
			this.my_modal_4.hide();
		}
	},
	mounted() {
		this.my_modal_1 = new Modal(document.getElementById("my-modal-1"));
		this.my_modal_2 = new Modal(document.getElementById("my-modal-2"));
		this.my_modal_3 = new Modal(document.getElementById("my-modal-3"));
		this.my_modal_4 = new Modal(document.getElementById("my-modal-4"));

		this.mqtt_status = this.$mqtt.status();

		// subscribe to spacecraft topic to get state updates
		this.$mqtt.subscribe("spacecraft", (message) => {
			try {
				let data = JSON.parse(message);
				const dt = new Date(data.ts*1000).toISOString(),
						dt_str = dt.replace('T', ' ').replace('Z','') + ' UTC';
				document.getElementById("dt-now").innerHTML = dt_str;

				if (data) {
					this.ul_state = data.ul_state;
					this.loading = false;
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
		SpaCon <small>Spacecraft Controller</small>
		<small class="float-end">
		</small>
	</h1>
	<hr class="mb-4">

	<div id="my-modal-1" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Command Sequence Uplink</h5>
				<button type="button" class="btn-close" @click="closeModal1()"></button>
			</div>
			<div class="modal-body">
				<div class="mb-3">
  					<label class="form-label" for="defaultFile">Choose file</label>
  					<input @change="onFileChange($event)" type="file" class="form-control">
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-outline-secondary" @click="closeModal1()">Cancel</button>
				<button @click="fileUpload('command-seq', $event)" type="button" class="btn btn-outline-theme">Uplink</button>
			</div>
			</div>
		</div>
	</div>

	<div id="my-modal-2" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Orbit Control Uplink</h5>
				<button type="button" class="btn-close" @click="closeModal2()"></button>
			</div>
			<div class="modal-body">
				<div class="mb-3">
  					<label class="form-label" for="defaultFile">Choose file</label>
  					<input @change="onFileChange($event)" type="file" class="form-control">
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-outline-secondary" @click="closeModal2()">Cancel</button>
				<button @click="fileUpload('orbit-control', $event)" type="button" class="btn btn-outline-theme">Uplink</button>
			</div>
			</div>
		</div>
	</div>

	<div id="my-modal-3" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Science Sequence Uplink</h5>
				<button type="button" class="btn-close" @click="closeModal3()"></button>
			</div>
			<div class="modal-body">
				<div class="mb-3">
  					<label class="form-label" for="defaultFile">Choose file</label>
  					<input @change="onFileChange($event)" type="file" class="form-control">
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-outline-secondary" @click="closeModal3()">Cancel</button>
				<button @click="fileUpload('science-seq', $event)" type="button" class="btn btn-outline-theme">Uplink</button>
			</div>
			</div>
		</div>
	</div>

	<div id="my-modal-4" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Flight Dynamics TTQ Uplink</h5>
				<button type="button" class="btn-close" @click="closeModal4()"></button>
			</div>
			<div class="modal-body">
				<form>
					<div class="form-check" v-for="(d, index) in flight_dynamics" :key="index">
						<input class="form-check-input" type="radio" name="fd_ttq_select" :id="d.id" :value="d.id" :checked="index === 0">
						<label class="form-check-label" :for="d.id">TTQ from product:{{ d.id }}</label>
					</div>
				</form>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-outline-secondary" @click="closeModal4()">Cancel</button>
				<button @click="fileUpload('fd-ttq', $event)" type="button" class="btn btn-outline-theme">Uplink</button>
			</div>
			</div>
		</div>
	</div>

	<div class="row">
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TC Manual Stack</card-header>
				<card-body>
					<div class="row">
						<div class="col-xl-8 col-lg-8">
							<table id="manual-stack" class="table table-sm mb-2px small text-nowrap">
								<tbody>
									<tr v-for="(item, i) in manual_stack">
										<td :class="{ 'text-success': manual_stack[i].command != 'none', 'app-tc-loaded': manual_stack[i].command != 'none' }">{{ item.command }}</td>
										<td class="text-end">
											<a href="#" @click="delCommand(i)" v-if="item.command != 'none'">
											<i class="fas fa-times text-danger"></i></a>
										</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div class="col-xl-4 col-lg-4 text-center">
							<button @click="armButton" id="arm-button" type="button" class="btn btn-outline-warning ms-2 mt-2" :disabled="lenStack() == 0" style="width: 94px;">ARM</button>
							<button @click="goButton" id="go-button" type="button" class="btn btn-outline-success ms-2 mt-2" :disabled="!is_armed" style="width: 94px;">GO</button>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-6 col-lg-6">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TC History</card-header>
				<card-body>
					<table class="table table-sm mb-2px small text-nowrap">
						<tbody>
							<tr v-for="(item, i) in tc_history">
								<td>{{ item[0] }}</td>
								<td v-if="item[1] == '_'" class="text-end fw-bold">{{  item[1] }}</td>
								<td v-if="item[1] != '_'" v-html="item[1]" class="text-end fw-bold"></td>
							</tr>
						</tbody>
					</table>
				</card-body>
			</card>
		</div>
	</div>

	<div class="row">
		<div class="col-xl-8 col-lg-8">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TC Database</card-header>
				<card-body>
					<div class="row mt-1" v-if="renderComponent">
						<div class="col">
							<h6 class="mt-2 mb-0">AOCS</h6>
							<button @click="addStack('TC_AOCS_001', 'aocs_mode', 'SUN', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set AOCS Mode SUN">TC_AOCS_001</button>
							<button @click="addStack('TC_AOCS_002', 'aocs_mode', 'NADIR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set AOCS Mode NADIR">TC_AOCS_002</button>
							<button @click="addStack('TC_AOCS_011', 'aocs_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set AOCS Chain A">TC_AOCS_011</button>
							<button @click="addStack('TC_AOCS_012', 'aocs_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set AOCS Chain B">TC_AOCS_012</button>
							<button @click="addStack('TC_AOCS_021', 'aocs_valid', 'valid', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Calibrate AOCS sensors">TC_AOCS_021</button>
						</div>
						<div class="col">
							<h6 class="mt-2 mb-0">TTC</h6>
							<button @click="addStack('TC_TTC_001', 'ttc_mode', 'S_Sup_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode S_Sup_LBR">TC_TTC_001</button>
							<button @click="addStack('TC_TTC_002', 'ttc_mode', 'S_Sup_HBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode S_Sup_HBR">TC_TTC_002</button>
							<button @click="addStack('TC_TTC_003', 'ttc_mode', 'X_Sup_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode X_Sup_LBR">TC_TTC_003</button>
							<button @click="addStack('TC_TTC_004', 'ttc_mode', 'X_Sup_HBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode X_Sup_HBR">TC_TTC_004</button>
							<button @click="addStack('TC_TTC_005', 'ttc_mode', 'S_Res_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode S_Res_LBR">TC_TTC_005</button>
							<button @click="addStack('TC_TTC_006', 'ttc_mode', 'X_Res_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode X_Res_LBR">TC_TTC_006</button>
							<button @click="addStack('TC_TTC_007', 'ttc_mode', 'S_Sub_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode S_Sub_LBR">TC_TTC_007</button>
							<button @click="addStack('TC_TTC_008', 'ttc_mode', 'X_Sub_LBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Mode X_Sub_LBR">TC_TTC_008</button>
							<button @click="addStack('TC_TTC_011', 'ttc_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Chain A">TC_TTC_011</button>
							<button @click="addStack('TC_TTC_012', 'ttc_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Chain B">TC_TTC_012</button>
							<button @click="addStack('TC_TTC_021', 'ttc_ping_ack', '', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Ping Spacecraft">TC_TTC_021</button>
						</div>
						<div class="col">
							<h6 class="mt-2 mb-0">TTC</h6>
							<button @click="addStack('TC_TTC_022', 'ttc_coherent', 'enabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Enable Coherent Transponder">TC_TTC_022</button>
							<button @click="addStack('TC_TTC_022', 'ttc_coherent', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Disable Coherent Transponder">TC_TTC_023</button>
							<button @click="addStack('TC_TTC_031', 'ttc_tx_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power Transmitter ON">TC_TTC_031</button>
							<button @click="addStack('TC_TTC_032', 'ttc_tx_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power Transmitter OFF">TC_TTC_032</button>
							<button @click="addStack('TC_TTC_041', 'ttc_obc_reboot', '', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Reboot OBC">TC_TTC_041</button>
							<button @click="addStack('TC_TTC_051', 'ttc_s_antenna', 'LGA_RHC', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Sb Antenna LGA RHC">TC_TTC_051</button>
							<button @click="addStack('TC_TTC_052', 'ttc_s_antenna', 'LGA_LHC', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Sb Antenna LGA LHC">TC_TTC_052</button>
							<button @click="addStack('TC_TTC_053', 'ttc_x_antenna', 'MGA', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Xb Antenna MGA">TC_TTC_053</button>
							<button @click="addStack('TC_TTC_054', 'ttc_x_antenna', 'HGA', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set TTC Xb Antenna HGA">TC_TTC_054</button>
							<button @click="addStack('TC_TTC_061', 'ttc_ranging', 'enabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Enable Ranging">TC_TTC_061</button>
							<button @click="addStack('TC_TTC_062', 'ttc_ranging', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Disable Ranging">TC_TTC_062</button>
						</div>
						<div class="col">
							<h6 class="mt-2 mb-0">EPS</h6>
							<button @click="addStack('TC_EPS_001', 'eps_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set EPS Chain A">TC_EPS_001</button>
							<button @click="addStack('TC_EPS_002', 'eps_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set EPS Chain B">TC_EPS_002</button>
							<button @click="addStack('TC_EPS_011', 'eps_sol_array__0', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Enable Solar Array 1">TC_EPS_011</button>
							<button @click="addStack('TC_EPS_012', 'eps_sol_array__0', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Disable Solar Array 1">TC_EPS_012</button>
							<button @click="addStack('TC_EPS_021', 'eps_sol_array__1', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Enable Solar Array 2">TC_EPS_021</button>
							<button @click="addStack('TC_EPS_022', 'eps_sol_array__1', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Disable Solar Array 2">TC_EPS_022</button>
						</div>
						<div class="col">
							<h6 class="mt-2 mb-0">DHS</h6>
							<button @click="addStack('TC_DHS_001', 'dhs_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set DHS Chain A">TC_DHS_001</button>
							<button @click="addStack('TC_DHS_002', 'dhs_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set DHS Chain B">TC_DHS_002</button>
							<button @click="addStack('TC_DHS_011', 'dhs_obsw_mode', 'safe', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set OBSW to Safe Mode">TC_DHS_011</button>
							<button @click="addStack('TC_DHS_012', 'dhs_obsw_mode', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Set OBSW to Nominal Mode">TC_DHS_012</button>
							<button @click="addStack('TC_DHS_021', 'dhs_mem_dump_enabled', true, $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Enable Memory Dump">TC_DHS_021</button>
							<button @click="addStack('TC_DHS_022', 'dhs_mem_dump_enabled', false, $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Disable Memory Dump">TC_DHS_022</button>
						</div>
						<div class="col">
							<h6 class="mt-2 mb-0">Payload</h6>
							<button @click="addStack('TC_PL_001', 'pl_gps_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power On GPS Receiver">TC_PL_001</button>
							<button @click="addStack('TC_PL_002', 'pl_gps_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power Off GPS Receiver">TC_PL_002</button>
							<button @click="addStack('TC_PL_011', 'pl_camera_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power On Camera">TC_PL_011</button>
							<button @click="addStack('TC_PL_012', 'pl_camera_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-1 mt-2" title="Power Off Camera">TC_PL_012</button>
							<button @click="addStack('TC_PL_021', 'pl_sdr_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" title="Power On SDR">TC_PL_021</button>
							<button @click="addStack('TC_PL_022', 'pl_sdr_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-1 mt-2" title="Power Off SDR">TC_PL_022</button>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">CFDP Files Uplink Service</card-header>
				<card-body class="text-center">
					<div class="row">
						<div class="col">
							<button type="button" class="btn btn-sm btn-outline-theme m-1 app-my-width" @click="openModal1()">Command<br/>Sequence</button>
						</div>
						<div class="col">
							<button type="button" class="btn btn-sm btn-outline-theme m-1 app-my-width" @click="openModal2()">Orbit<br/>Control</button>
						</div>
					</div>
					<div class="row">
						<div class="col">
							<button type="button" class="btn btn-sm btn-outline-theme m-1 app-my-width" @click="openModal3()">Science<br/>Sequence</button>
						</div>
						<div class="col">
							<button type="button" class="btn btn-sm btn-outline-theme m-1 app-my-width" @click="openModal4()">Flight<br/>Dynamics</button>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>

</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
.app-my-width { width: 120px; }
tr:has(.app-tc-loaded) { border-bottom: 1px solid #3cd2a5; }
tr:has(.app-tc-armed) { border-bottom: 1px solid #ff9f0c; }
</style>