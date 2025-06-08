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
			data: [],
			loading: false,
			error: null,
			packet: null
		};
	},
	mounted() {
		this.my_modal_1 = new Modal(document.getElementById("my-modal-1"));

		this.fetchData();
	},
	methods: {
		fetchData() {
			this.loading = true;
			
			axios.get(`${appOption.soAPI}/obj-store/tm`)
				.then(response => {
					this.data = response.data;
				})
				.catch(error => {
					this.error = error;
				})
				.finally(() => {
					this.loading = false;
				});
		},
		packetDetails(bucket, object_name) {
			axios.get(`${appOption.soAPI}/obj-store/sp/${bucket}/${object_name}`)
				.then(response => {
					this.packet = response.data;
				})
				.catch(error => {
					this.error = error;
				})
				.finally(() => {
					this.loading = false;
					this.my_modal_1.show();
				});
			this.my_modal_1.show();
		},
		openModal1() {
			this.my_modal_1.show();
		},
		closeModal1() {
			this.my_modal_1.hide();
		},
	}
}

</script>
<template>
	<div id="my-modal-1" class="modal">
		<div class="modal-dialog modal-lg">
			<div class="modal-content">
			<div class="modal-header">
				<h5 class="modal-title">Space Packet</h5>
				<button type="button" class="btn-close" @click="closeModal1()"></button>
			</div>
			<div class="modal-body" v-if="packet">
				<h5 class="text-muted border-bottom">Primary Header</h5>
				<div class="row small text-secondary mb-3">
					<div class="col-3">Version<br/><code>{{ packet.primary_header.version }}</code></div>
					<div class="col-3">Type<br/><code>{{ packet.primary_header.type }}</code></div>
					<div class="col-3">Sec. Hdr.<br/><code>{{ packet.primary_header.sec_hdr_flag }}</code></div>
					<div class="col-3">APID<br/><code>{{ packet.primary_header.apid }}</code></div>
					<div class="col-3">Seq. Flags<br/><code>{{ packet.primary_header.sequence_flags }}</code></div>
					<div class="col-3">Seq. Count<br/><code>{{ packet.primary_header.sequence_count }}</code></div>
					<div class="col-3">Data Length<br/><code>{{ packet.primary_header.data_length }}</code></div>
				</div>
				<h5 class="text-muted border-bottom">Payload</h5>
				<div class="row small text-secondary">
					<div class="col-2">Time Step<br/><code>{{ packet.payload.ts }}</code></div>
					<div class="col-2">AOCS Chain<br/><code>{{ packet.payload.aocs_chain }}</code></div>
					<div class="col-2">AOCS Mode<br/><code>{{ packet.payload.aocs_mode }}</code></div>
					<div class="col-2">AOCS Valid<br/><code>{{ packet.payload.aocs_valid }}</code></div>
					<div class="col-2">AOCS Rotation X<br/><code>{{ packet.payload.aocs_rotation_x.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Rotation Y<br/><code>{{ packet.payload.aocs_rotation_y.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Rotation Z<br/><code>{{ packet.payload.aocs_rotation_z.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Rate X<br/><code>{{ packet.payload.aocs_rate_x.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Rate Y<br/><code>{{ packet.payload.aocs_rate_y.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Rate Z<br/><code>{{ packet.payload.aocs_rate_z.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Sun Ang.<br/><code>{{ packet.payload.aocs_sun_angle.toFixed(6) }}</code></div>
					<div class="col-2">AOCS Nadir Ang.<br/><code>{{ packet.payload.aocs_nadir_angle.toFixed(6) }}</code></div>
					<div class="col-2">TTC Chain<br/><code>{{ packet.payload.ttc_chain }}</code></div>
					<div class="col-2">TTC OBC<br/><code>{{ packet.payload.ttc_obc }}</code></div>
					<div class="col-2">TTC Mode<br/><code>{{ packet.payload.ttc_mode }}</code></div>
					<div class="col-2">TTC Sb Antenna<br/><code>{{ packet.payload.ttc_s_antenna }}</code></div>
					<div class="col-2">TTC Xb Antenna<br/><code>{{ packet.payload.ttc_x_antenna }}</code></div>
					<div class="col-2">TTC SNR UL<br/><code>{{ packet.payload.ttc_snr_ul.toFixed(6) }}</code></div>
					<div class="col-2">TTC State UL<br/><code>{{ packet.payload.ttc_state_ul }}</code></div>
					<div class="col-2">TTC Coherent<br/><code>{{ packet.payload.ttc_coherent }}</code></div>
					<div class="col-2">TTC TX Status<br/><code>{{ packet.payload.ttc_tx_status }}</code></div>
					<div class="col-2">TTC Ping Ack.<br/><code>{{ packet.payload.ttc_ping_ack }}</code></div>
					<div class="col-2">TTC Ranging<br/><code>{{ packet.payload.ttc_ranging }}</code></div>
					<div class="col-2">EPS Chain<br/><code>{{ packet.payload.eps_chain }}</code></div>
					<div class="col-2">EPS Net Power<br/><code>{{ packet.payload.eps_net_power.toFixed(6) }}</code></div>
					<div class="col-2">EPS Sol. Arr. 1<br/><code>{{ packet.payload.eps_sol_array_1 }}</code></div>
					<div class="col-2">EPS Sol. Arr. 2<br/><code>{{ packet.payload.eps_sol_array_2 }}</code></div>
					<div class="col-2">EPS Batt. DOD<br/><code>{{ packet.payload.eps_battery_dod.toFixed(6) }}</code></div>
					<div class="col-2">EPS Temperature<br/><code>{{ packet.payload.eps_temperature.toFixed(6) }}</code></div>
					<div class="col-2">EPS ACU<br/><code>{{ packet.payload.eps_acu }}</code></div>
					<div class="col-2">EPS PDU<br/><code>{{ packet.payload.eps_pdu }}</code></div>
					<div class="col-2">DHS Chain<br/><code>{{ packet.payload.dhs_chain }}</code></div>
					<div class="col-2">DHS OBSW Mode<br/><code>{{ packet.payload.dhs_obsw_mode }}</code></div>
					<div class="col-2">DHS Mem. Dump<br/><code>{{ packet.payload.dhs_mem_dump_enabled }}</code></div>
					<div class="col-2">DHS Memory<br/><code>{{ packet.payload.dhs_memory.toFixed(6) }}</code></div>
					<div class="col-2">DHS TM Count<br/><code>{{ packet.payload.dhs_tm_counter }}</code></div>
					<div class="col-2">DHS TC Count<br/><code>{{ packet.payload.dhs_tc_counter }}</code></div>
					<div class="col-2">PL GPS<br/><code>{{ packet.payload.pl_gps_status }}</code></div>
					<div class="col-2">PL GPS Lat<br/><code>{{ packet.payload.pl_gps_lat }}</code></div>
					<div class="col-2">PL GPS Lon<br/><code>{{ packet.payload.pl_gps_lon }}</code></div>
					<div class="col-2">PL GPS Alt<br/><code>{{ packet.payload.pl_gps_alt }}</code></div>
					<div class="col-2">PL Camera<br/><code>{{ packet.payload.pl_camera_status }}</code></div>
					<div class="col-2">PL SDR<br/><code>{{ packet.payload.pl_sdr_status }}</code></div>
				</div>
			</div>
			<div class="modal-footer">
				<button type="button" class="btn btn-outline-secondary" @click="closeModal1()">Close</button>
			</div>
			</div>
		</div>
	</div>

	<h1 class="page-header">Packet Store <small>Space Packets</small></h1>
	<hr class="mb-4">

	<div v-if="renderComponent && loading">
		Loading ...
	</div>

	<div v-if="renderComponent && !loading">
		<card class="mb-3" v-for="d in data">
			<card-header class="fw-bold">PASS {{ d.bucket.replace("-tm", " TELEMETRY") }}</card-header>
			<card-body class="mb-1">
				<div class="row">
  					<div class="col-4 pointer" v-for="(item, index) in d.data" :key="index" @click="packetDetails(d.bucket, item)">
						<div class="border-bottom m-1 small">
							<code>SpacePacket(type=TM, apid=10)</code><br/><span class="text-secondary text-end"> @{{ item }}</span>
						</div>
					</div>
				</div>
			</card-body>
		</card>

		<p v-if="data && data.length === 0">No packets found.</p>
	</div>

</template>
<style>
.pointer:hover { background-color: rgba(87, 87, 87, 0.348); cursor: pointer; }
</style>