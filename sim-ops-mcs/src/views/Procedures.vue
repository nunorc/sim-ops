<script>
import { useAppVariableStore } from '@/stores/app-variable';
import apexchart from '@/components/plugins/Apexcharts.vue';
import jsVectorMap from 'jsvectormap';
import 'jsvectormap/dist/maps/world.js';
import 'jsvectormap/dist/css/jsvectormap.min.css';
import axios from 'axios';

const appVariable = useAppVariableStore();

export default {
	components: {
		
	},
	data() {
		let establishUplink = [
			{ 'num' : '1', 'con': '', 'action': 'enable program track', 'tc': 'OM > Program Track'},
			{ 'num' : '2', 'con': '', 'action': 'check GS U/L power', 'tc': 'OM > U/L Power'},
			{ 'num' : '3', 'con': 'Requires elevation above 5°', 'action': 'enable carrier', 'tc': 'OM > U/L Carrier'},
			{ 'num' : '4', 'con': '', 'action': 'sweep', 'tc': 'OM > Sweep'}
		];
		let establishDownlink = [
			{ 'num' : '1', 'con': '', 'action': 'enable program track', 'tc': 'OM > Program Track'},
			{ 'num' : '2', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '3', 'con': 'onboard TX off', 'action': 'enable on-board Transmitter', 'tc': 'TC_TTC_031'},
			{ 'num' : '4', 'con': '', 'action': 'determine current TTC mode from expected value, SNR and spectrum', 'tc': 'OM > D/L Spectrum'},
			{ 'num' : '5', 'con': '', 'action': 'select the onboard TTC mode on G/S', 'tc': 'OM > Mode'}
		];
		let enableRanging = [
			{ 'num' : '1', 'con': 'No U/L Frame Lock', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'No D/L Frame Lock', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'enable ranging', 'tc': 'OM > Enable Ranging'},
		];
		let enableDoppler = [
			{ 'num' : '1', 'con': 'No U/L Frame Lock', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'No D/L Frame Lock', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'set transponder coherent', 'tc': 'TC_TTC_022'},
			{ 'num' : '4', 'con': '', 'action': 'enable doppler', 'tc': 'OM > Enable Doppler'}
		];
		let changeTtcMode =[
			{ 'num' : '1', 'con': 'No U/L Frame Lock', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'No D/L Frame Lock', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'set desired TTC Mode', 'tc': 'TC_TTC_00X'},
			{ 'num' : '4', 'con': '', 'action': 'set desired TTC Mode in G/S', 'tc': 'OM > Mode'}
		];
		let downloadData = [
			{ 'num' : '1', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'Downlink not yet established', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'set AOCS to Nadir Pointing', 'tc': 'TC_AOCS_002'},
			{ 'num' : '4', 'con': 'SNR Margin above 3dB', 'action': 'change TTC Mode to XLBR', 'tc': 'TC_TTC_003'},
			{ 'num' : '5', 'con': '', 'action': 'change GS Mode to XLBR', 'tc': 'OM > Mode'},
			{ 'num' : '6', 'con': '', 'action': 'start download', 'tc': 'TC_DHS_021'},
			{ 'num' : '7', 'con': 'SNR Margin above 3dB', 'action': 'change TTC Mode to XHBR', 'tc': 'TC_TTC_004'},
			{ 'num' : '8', 'con': '', 'action': 'change GS Mode to XHBR', 'tc': 'OM > Mode'},
			{ 'num' : '9', 'con': '', 'action': 'restart download', 'tc': 'TC_DHS_021'},
			{ 'num' : '10', 'con': 'Frame Lock lost', 'action': 'change TTC Mode to XLBR', 'tc': 'TC_TTC_003'},
			{ 'num' : '11', 'con': '', 'action': 'restart download', 'tc': 'TC_DHS_021'},
			{ 'num' : '12', 'con': '', 'action': 'change GS Mode to XLBR', 'tc': 'OM > Mode'},
			{ 'num' : '13', 'con': 'Frame Lock lost', 'action': 'change TTC Mode to SHBR', 'tc': 'TC_TTC_002'},
			{ 'num' : '14', 'con': '', 'action': 'change GS Mode to SHBR', 'tc': 'OM > Mode'}
		];
		let recoverSafeMode = [
			{ 'num' : '1', 'con': '', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': '', 'action': 'change TTC Mode to SLBR on G/S', 'tc': 'OM > Mode'},
			{ 'num' : '3', 'con': '', 'action': 'enable on-board Transmitter', 'tc': 'TC_TTC_031'},
			{ 'num' : '4', 'con': '', 'action': 'confirm safemode', 'tc': 'DHS > OBSW Mode'},
			{ 'num' : '5', 'con': '', 'action': 'set OBSW mode to nominal', 'tc': 'TC_DHS_012'},
			{ 'num' : '6', 'con': '', 'action': 'set AOCS Chain to A', 'tc': 'TC_AOCS_011'},
			{ 'num' : '7', 'con': '', 'action': 'set TTC Chain to A', 'tc': 'TC_TTC_011'},
			{ 'num' : '8', 'con': '', 'action': 'set PTS Chain to A', 'tc': 'TC_PTS_001'},
			{ 'num' : '9', 'con': '', 'action': 'set DHS Chain to A', 'tc': 'TC_DHS_001'},
			{ 'num' : '10', 'con': '', 'action': 'set TTC Mode to SHBR', 'tc': 'TC_TTC_002'}
		];
		let switchOnGPS = [
			{ 'num' : '1', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'Downlink not yet established', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power on GPS receiver', 'tc': 'TC_PL_001'}
		];
		let switchOffGPS = [
			{ 'num' : '1', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'Downlink not yet established', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power off GPS receiver', 'tc': 'TC_PL_002'}
		];
		let switchOnCamera = [
			{ 'num' : '1', 'con': '', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': '', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power on camera', 'tc': 'TC_PL_011'}
		];
		let switchOffCamera = [
			{ 'num' : '1', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'Downlink not yet established', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power off camera', 'tc': 'TC_PL_012'}
		];
		let switchOnSDR = [
			{ 'num' : '1', 'con': '', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': '', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power on SDR', 'tc': 'TC_PL_021'}
		];
		let switchOffSDR = [
			{ 'num' : '1', 'con': 'Uplink not yet established', 'action': 'establish Uplink', 'tc': '<a href="#EstablishUplink">Establish Uplink</a>'},
			{ 'num' : '2', 'con': 'Downlink not yet established', 'action': 'establish Downlink', 'tc': '<a href="#EstablishDownlink">Establish Downlink</a>'},
			{ 'num' : '3', 'con': '', 'action': 'Power off SDR', 'tc': 'TC_PL_022'}
		];
		return {
			renderComponent: true,
			procedures: [establishUplink, establishDownlink, enableRanging, enableDoppler, changeTtcMode, downloadData, recoverSafeMode, switchOnGPS, switchOffGPS, switchOnCamera, switchOffCamera, switchOnSDR, switchOffSDR],
			procedurenames: ["Establish Uplink", "Establish Downlink", "Enable Ranging", "Enable Doppler", "Change TTC Mode", "Download OBC Data", "Recover from Safemode", "Power on GPS Receiver", "Power off GPS Receiver", "Power on Camera", "Power off Camera", "Power on SDR", "Power off SDR"]
		}
	},
	methods: {
		searchTable() {
			var input, filter, tables, table, tr, td, i, txtValue, found;
			input = document.getElementById("myInput");
			filter = input.value.toUpperCase();

			var divs = document.querySelectorAll(".for-loop");
			for (var i = 0; i < divs.length; i++) {
				var hdr = divs[i].getElementsByTagName("h4")[0],
				    txt = hdr.innerText.toUpperCase();

				if (txt.indexOf(filter) > -1)
					divs[i].style.display = "";
				else
					divs[i].style.display = "none";
			}
		}
	},
	mounted() {
		//this.updateProcedures();
	}
}
</script>
<template>
	<!-- BEGIN page-header -->
	<h1 class="page-header">
		Procedures <small>Operations Procedures</small>
		<small class="float-end">
			<span class="badge bg-dark">Database</span>
			<span class="badge bg-success">Online</span>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<!-- BEGIN table -->
	<div class="row">
		<div class="col-xl-2 col-lg-2 mb-4">
			<input id="myInput" @input="searchTable()" class="form-control" type="search" placeholder="Search">
		</div>
	</div>
	
	<div id="myTable" v-if="renderComponent" >
		<div class="for-loop" v-for="(procedure, index) in procedures" :id="procedurenames[index].replace(/ /g, '')">
			<h4 class="">{{ procedurenames[index] }}</h4>
			
			<table class="table table-bordered mb-3 table-striped">
				<thead>
					<tr class="text-center">
						<th class="text-center" style="width: 4%">#</th>
						<th class="text-start" style="width: 48%">Action</th>
						<th class="" style="">Condition</th>
						<th class="text-center" style="width: 20%;">TC</th>
					</tr>
				</thead>
				<tbody class="text-body">
					<tr v-if="procedure.length > 0" v-for="p in procedure">
						<td class="text-center">{{ p.num }}</td>
						<td class="text-capitalize">{{ p.action }}</td>
						<td class="text-center">{{ p.con }}</td>
						<td class="text-center text-capitalize" v-html="p.tc"></td> <!--Will render potentially unsafe code -->
					</tr>
				</tbody>
			</table>
		</div>
	</div>

</template>

<style>
html { scroll-padding-top: 64px; }
</style>