<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import apexchart from '@/components/plugins/Apexcharts.vue';
import jsVectorMap from 'jsvectormap';
import 'jsvectormap/dist/maps/world.js';
import 'jsvectormap/dist/css/jsvectormap.min.css';
import axios from 'axios';
import { Modal } from 'bootstrap';

const appVariable = useAppVariableStore(),
      appOption = useAppOptionStore();


export default {
	components: {
		apexchart: apexchart
	},
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
			mqtt_status: "checking"
		}
	},
	methods: {
		sendCommand(type) {
			let title = type;
			if (type=='db')
				title = document.getElementById("exampleFormControlSelect1").value

			let item = { title: title, time: 'just now', badge: 'QUEUE', highlight: false };
			this.activityLog.push(item);
		},
		disableButtons() {
			document.querySelectorAll(".btn-sm").forEach(element => {
				element.disabled = true;
			});
			document.getElementById("lock").classList.toggle('d-none');
			document.getElementById("lock-open").classList.toggle('d-none');
		},
		enableButtons() {
			document.querySelectorAll(".btn-sm").forEach(element => {
				element.disabled = false;
			});
			document.getElementById("lock").classList.toggle('d-none');
			document.getElementById("lock-open").classList.toggle('d-none');
		},
		sendCommand(command, control, value, event) {
			let button = event.target;

			button.disabled = true;
			this.control_send = `${command}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			let body = { 'system': 'spacecraft',  'control': control, 'value': value, 'command': command };
			axios.post(`${appOption.soAPI}/control`, body)
				.then((resp) => {
					this.control_recv = resp.data.status;
					button.disabled = false;
					this.control_recv_loading = false;
				})
		},
		fileUpload(type, event) {
			this.control_send = `upload ${type} ${this.file_upload}`;
			this.control_recv = '';
			this.control_recv_loading = true;

			this.closeModal1();
			this.closeModal2();
			this.closeModal3();

			let body = { 'system': 'spacecraft',  'control': 'dhs_uploaded', 'value': `${type} > ${this.file_upload}`, 'command': `uploaded: ${type} > ${this.file_upload}` };
			axios.post(`${appOption.soAPI}/control`, body)
				.then((resp) => {
					this.control_recv = resp.data.status;
					this.control_recv_loading = false;
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
		closeModal1() {
			this.my_modal_1.hide();
		},
		closeModal2() {
			this.my_modal_2.hide();
		},
		closeModal3() {
			this.my_modal_3.hide();
		}
	},
	mounted() {
		this.my_modal_1 = new Modal(document.getElementById("my-modal-1"));
		this.my_modal_2 = new Modal(document.getElementById("my-modal-2"));
		this.my_modal_3 = new Modal(document.getElementById("my-modal-3"));

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
	<!-- BEGIN page-header -->
	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		SpaCon <small>Spacecraft Controller</small>
		<small class="float-end">
			<!-- <span class="badge rounded-0 bg-secondary">U/L State</span>
			<span v-if="ul_state" class="badge rounded-0 text-uppercase" :class="{ 'text-bg-danger': ul_state==='NO_RF', 'text-bg-warning': ul_state==='PLL_LOCK' || ul_state==='PSK_LOCK' || ul_state==='BIT_LOCK', 'text-bg-success': ul_state==='FRAME_LOCK' }">{{ ul_state }}</span>
			<span v-else class="badge rounded-0 bg-dark">_</span> -->
			<button @click="enableButtons" type="button" class="btn btn btn-outline-warning visible ms-2" id="lock" style="width: 84px;">ARM</button>
			<button @click="disableButtons" type="button" class="btn btn btn-outline-theme visible d-none ms-2" id="lock-open" style="width: 84px;">DISARM</button>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<div id="my-modal-1" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Attitude Control Upload</h5>
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
				<button @click="fileUpload('attitude-control', $event)" type="button" class="btn btn-outline-theme">Upload</button>
			</div>
			</div>
		</div>
	</div>

	<div id="my-modal-2" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Orbit Control Upload</h5>
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
				<button @click="fileUpload('orbit-control', $event)" type="button" class="btn btn-outline-theme">Upload</button>
			</div>
			</div>
		</div>
	</div>

	<div id="my-modal-3" class="modal">
		<div class="modal-dialog">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">CFDP Science Control Upload</h5>
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
				<button @click="fileUpload('science-control', $event)" type="button" class="btn btn-outline-theme">Upload</button>
			</div>
			</div>
		</div>
	</div>
<div class="row">
<div class="col-xl-12 col-lg-12">
<card class="mb-3">
<card-header class="card-header fw-bold small text-center p-1">TC Send</card-header>
<card-body>
	<div class="row mt-1" v-if="renderComponent">
		<div class="col">
			<h6 class="mt-2 mb-0">AOCS</h6>
			<button @click="sendCommand('TC_AOCS_001', 'aocs_mode', 'SUN', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="AOCS Mode SUN">TC_AOCS_001</button>
			<!-- <button @click="sendCommand('TC_AOCS_002', 'aocs_mode', 'TARGET', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled>TC_AOCS_002</button> -->
			<button @click="sendCommand('TC_AOCS_002', 'aocs_mode', 'NADIR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="AOCS Mode NADIR">TC_AOCS_002</button>
			<!-- <button @click="sendCommand('TC_AOCS_004', 'aocs_mode', 'RATEDAMPING', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled>TC_AOCS_004</button> -->
			<!-- <button @click="sendCommand('TC_AOCS_005', 'aocs_mode', 'MONITORING', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled>TC_AOCS_005</button> -->
			<button @click="sendCommand('TC_AOCS_011', 'aocs_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="AOCS Chain A">TC_AOCS_011</button>
			<button @click="sendCommand('TC_AOCS_012', 'aocs_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="AOCS Chain B">TC_AOCS_012</button>
		</div>
	</div>
	<div class="row mt-1" v-if="renderComponent">
		<div class="col">
			<h6 class="mt-2 mb-0">TTC</h6>
			<button @click="sendCommand('TC_TTC_001', 'ttc_mode', 'SLBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC SLBR">TC_TTC_001</button>
			<button @click="sendCommand('TC_TTC_002', 'ttc_mode', 'SHBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC SHBR">TC_TTC_002</button>
			<button @click="sendCommand('TC_TTC_003', 'ttc_mode', 'XLBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC XLBR">TC_TTC_003</button>
			<button @click="sendCommand('TC_TTC_004', 'ttc_mode', 'XHBR', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC XHBR">TC_TTC_004</button>
			<button @click="sendCommand('TC_TTC_011', 'ttc_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC Chain A">TC_TTC_011</button>
			<button @click="sendCommand('TC_TTC_012', 'ttc_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="TTC Chain B">TC_TTC_012</button>
			<button @click="sendCommand('TC_TTC_021', 'ttc_ping_ack', '', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Ping">TC_TTC_021</button>
			<button @click="sendCommand('TC_TTC_022', 'ttc_coherent', true, $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Set Coherent">TC_TTC_022</button>
			<button @click="sendCommand('TC_TTC_031', 'ttc_tx_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Transmitter ON">TC_TTC_031</button>
			<button @click="sendCommand('TC_TTC_032', 'ttc_tx_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Transmitter OFF">TC_TTC_032</button>
		</div>
	</div>
	<div class="row mt-1" v-if="renderComponent">
		<div class="col">
			<h6 class="mt-2 mb-0">PTS</h6>
			<button @click="sendCommand('TC_PTS_001', 'pts_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="PTS Chain A">TC_PTS_001</button>
			<button @click="sendCommand('TC_PTS_002', 'pts_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="PTS Chain B">TC_PTS_002</button>
			<button @click="sendCommand('TC_PTS_011', 'pts_sol_array__0', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Enable Array 1">TC_PTS_011</button>
			<button @click="sendCommand('TC_PTS_012', 'pts_sol_array__0', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Disable Array 1">TC_PTS_012</button>
			<button @click="sendCommand('TC_PTS_021', 'pts_sol_array__1', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Enable Array 2">TC_PTS_021</button>
			<button @click="sendCommand('TC_PTS_022', 'pts_sol_array__1', 'disabled', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Disable Array 2">TC_PTS_022</button>
		</div>
	</div>
	<div class="row mt-1" v-if="renderComponent">
		<div class="col">
			<h6 class="mt-2 mb-0">DHS</h6>
			<button @click="sendCommand('TC_DHS_001', 'dhs_chain', 'A', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="DHS Chain A">TC_DHS_001</button>
			<button @click="sendCommand('TC_DHS_002', 'dhs_chain', 'B', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="DHS Chain B">TC_DHS_002</button>
			<button @click="sendCommand('TC_DHS_011', 'dhs_obsw_mode', 'safe', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Safe Mode">TC_DHS_011</button>
			<button @click="sendCommand('TC_DHS_012', 'dhs_obsw_mode', 'nominal', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Nominal Mode">TC_DHS_012</button>
			<button @click="sendCommand('TC_DHS_021', 'dhs_mem_dump_enabled', true, $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Start Memory Dump">TC_DHS_021</button>
			<button @click="sendCommand('TC_DHS_022', 'dhs_mem_dump_enabled', false, $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Stop Memory Dump">TC_DHS_022</button>
		</div>
	</div>
	<div class="row mt-1" v-if="renderComponent">
		<div class="col">
			<h6 class="mt-2 mb-0">Payload</h6>
			<button @click="sendCommand('TC_PL_001', 'pl_gps_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="GPS ON">TC_PL_001</button>
			<button @click="sendCommand('TC_PL_002', 'pl_gps_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="GPS OFF">TC_PL_002</button>
			<button @click="sendCommand('TC_PL_011', 'pl_camera_status', 'on', $event)" type="button" class="btn btn-sm btn-outline-theme me-2 mt-2" disabled v-b-tooltip.hover title="Camera ON">TC_PL_011</button>
			<button @click="sendCommand('TC_PL_012', 'pl_camera_status', 'off', $event)" type="button" class="btn btn-sm btn-outline-theme me-1 mt-2" disabled v-b-tooltip.hover title="Camera OFF">TC_PL_012</button>
		</div>
	</div>
</card-body>
</card>
</div>
</div>

	<div class="row mt-2" v-if="renderComponent">
		<div class="col-xl-8 col-lg-8">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">DHS CFDP Command Files Upload</card-header>
				<card-body class="text-center">
					<button type="button" class="btn btn-sm btn-outline-theme" @click="openModal1()" disabled>Attitude Control</button>
					<span>&nbsp;&nbsp;</span>
					<button type="button" class="btn btn-sm btn-outline-theme" @click="openModal2()" disabled>Orbit Control</button>
					<span>&nbsp;&nbsp;</span>
					<button type="button" class="btn btn-sm btn-outline-theme" @click="openModal3()" disabled>Science Control</button>
				</card-body>
			</card>
		</div>
		<div class="col-xl-4 col-lg-4">
			<card class="mb-3">
				<card-header class="card-header fw-bold small text-center p-1">TC Console</card-header>
				<card-body class="p-1 mx-2">
					<table class="table table-sm table-striped table-borderless mb-2px small text-nowrap">
						<tbody>
							<tr><td><span>&nbsp;[Send]&nbsp;</span><span>{{ control_send }}</span></td></tr>
							<tr><td><span>&nbsp;[Recv]&nbsp;</span>
								<span v-if="control_recv_loading" class="spinner-border spinner-border-sm text-secondary" role="status"><span class="visually-hidden">Loading...</span></span>
								<!-- <span class="fw-bold" :class="{ 'text-theme': control_recv==='OK', 'text-danger': control_recv!=='OK'}">{{ control_recv }}</span> -->
								<span v-if="control_recv.length>0" class="fw-bold" :class="{ 'text-theme': control_recv.split(' ')[0].split(':')[0]==='g', 'text-danger': control_recv.split(' ')[0].split(':')[0]==='r'}">{{ control_recv.split(' ')[0].split(':')[1] }}</span>&nbsp;
								<span v-if="control_recv.length>0" class="fw-bold" :class="{ 'text-theme': control_recv.split(' ')[1].split(':')[0]==='g', 'text-danger': control_recv.split(' ')[1].split(':')[0]==='r', 'text-warning': control_recv.split(' ')[2].split(':')[0]==='w'}">{{ control_recv.split(' ')[1].split(':')[1] }}</span>&nbsp;
								<span v-if="control_recv.length>0" class="fw-bold" :class="{ 'text-theme': control_recv.split(' ')[2].split(':')[0]==='g', 'text-danger': control_recv.split(' ')[2].split(':')[0]==='r', 'text-warning': control_recv.split(' ')[2].split(':')[0]==='w' }">{{ control_recv.split(' ')[2].split(':')[1] }}</span>
							</td></tr>
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