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
		return {
			renderComponent: true,
			commands: [
				{ 'sub': 'AOCS', 'desc': 'Set AOCS mode SUN', 'tc': 'TC_AOCS_001', 'tm': 'AOCS > AOCS Mode' },
				// { 'sub': 'AOCS', 'desc': 'Set AOCS mode TARGET', 'tc': 'TC_AOCS_002', 'tm': 'AOCS > AOCS Mode' },
				{ 'sub': 'AOCS', 'desc': 'Set AOCS mode NADIR', 'tc': 'TC_AOCS_002', 'tm': 'AOCS > AOCS Mode' },
				// { 'sub': 'AOCS', 'desc': 'Set AOCS mode RATEDAMPING', 'tc': 'TC_AOCS_004', 'tm': 'AOCS > AOCS Mode' },
				// { 'sub': 'AOCS', 'desc': 'Set AOCS mode MONITORING', 'tc': 'TC_AOCS_005', 'tm': 'AOCS > AOCS Mode' },
				{ 'sub': 'AOCS', 'desc': 'Set AOCS chain A', 'tc': 'TC_AOCS_011', 'tm': 'AOCS > AOCS Chain' },
				{ 'sub': 'AOCS', 'desc': 'Set AOCS chain B', 'tc': 'TC_AOCS_012', 'tm': 'AOCS > AOCS Chain' },

				{ 'sub': 'TTC', 'desc': 'Set TTC mode SLBR', 'tc': 'TC_TTC_001', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode SHBR', 'tc': 'TC_TTC_002', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode XLBR', 'tc': 'TC_TTC_003', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode XHBR', 'tc': 'TC_TTC_004', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC chain A', 'tc': 'TC_TTC_011', 'tm': 'TTC > TTC Chain' },
				{ 'sub': 'TTC', 'desc': 'Set TTC chain B', 'tc': 'TC_TTC_012', 'tm': 'TTC > TTC Chain' },
				{ 'sub': 'TTC', 'desc': 'Ping spacecraft', 'tc': 'TC_TTC_021', 'tm': 'TTC > TTC Pink Ack' },
				{ 'sub': 'TTC', 'desc': 'Set coherent transponder', 'tc': 'TC_TTC_022', 'tm': 'TTC > TTC Coherent' },
				{ 'sub': 'TTC', 'desc': 'Set Transmitter ON', 'tc': 'TC_TTC_031', 'tm': 'TTC > TTC TX status' },
				{ 'sub': 'TTC', 'desc': 'Set Transmitter OFF', 'tc': 'TC_TTC_032', 'tm': 'TTC > TTC TX status' },

				{ 'sub': 'PTS', 'desc': 'Set PTS chain A', 'tc': 'TC_PTS_001', 'tm': 'PTS > PTS Chain' },
				{ 'sub': 'PTS', 'desc': 'Set PTS chain B', 'tc': 'TC_PTS_002', 'tm': 'PTS > PTS Chain' },
				{ 'sub': 'PTS', 'desc': 'Enable solar Array 1', 'tc': 'TC_PTS_011', 'tm': 'PTS > Solar Array 1' },
				{ 'sub': 'PTS', 'desc': 'Disable solar Array 1', 'tc': 'TC_PTS_012', 'tm': 'PTS > Solar Array 1' },
				{ 'sub': 'PTS', 'desc': 'Enable solar Array 2', 'tc': 'TC_PTS_021', 'tm': 'PTS > Solar Array 2' },
				{ 'sub': 'PTS', 'desc': 'Disable solar Array 2', 'tc': 'TC_PTS_022', 'tm': 'PTS > Solar Array 2' },

				{ 'sub': 'DHS', 'desc': 'Set DHS chain A', 'tc': 'TC_DHS_001', 'tm': 'DHS > DHS Chain' },
				{ 'sub': 'DHS', 'desc': 'Set DHS chain B', 'tc': 'TC_DHS_002', 'tm': 'DHS > DHS Chain' },
				{ 'sub': 'DHS', 'desc': 'Set OBSW to safe mode', 'tc': 'TC_DHS_011', 'tm': 'DHS > OBSW Mode' },
				{ 'sub': 'DHS', 'desc': 'Set OBSW to nominal mode', 'tc': 'TC_DHS_012', 'tm': 'DHS > OBSW Mode' },
				{ 'sub': 'DHS', 'desc': 'Enable memory downlink dump', 'tc': 'TC_DHS_021', 'tm': 'DHS > Memory Dump' },
				{ 'sub': 'DHS', 'desc': 'Disable memory downlink dump', 'tc': 'TC_DHS_022', 'tm': 'DHS > Memory Dump' },

				{ 'sub': 'Payload', 'desc': 'Power on GPS receiver', 'tc': 'TC_PL_001', 'tm': 'Payload > GPS Status' },
				{ 'sub': 'Payload', 'desc': 'Power off GPS receiver', 'tc': 'TC_PL_002', 'tm': 'Payload > GPS Status' },
				{ 'sub': 'Payload', 'desc': 'Power on camera', 'tc': 'TC_PL_011', 'tm': 'Payload > Camera Status' },
				{ 'sub': 'Payload', 'desc': 'Power off camera', 'tc': 'TC_PL_012', 'tm': 'Payload > Camera Status' },
				{ 'sub': 'Payload', 'desc': 'Power on SDR', 'tc': 'TC_PL_021', 'tm': 'Payload > SDR Status' },
				{ 'sub': 'Payload', 'desc': 'Power off SDR', 'tc': 'TC_PL_022', 'tm': 'Payload > SDR Status' }
			]
		}
	},
	methods: {
		searchTable() {
			// Declare variables
			var input, filter, table, tr, td, i, txtValue, found;
			input = document.getElementById("myInput");
			filter = input.value.toUpperCase();
			table = document.getElementById("myTable");
			console.log('filter: ' + filter);

			// Loop through all table rows, and hide those who don't match the search query
			for (var i = 1, row; row = table.rows[i]; i++) {
				found = false;
				for (var j = 0, col; col = row.cells[j]; j++) {
					if (col) {
						txtValue = col.textContent || col.innerText;
						if (txtValue.toUpperCase().indexOf(filter) > -1)
							found = true;
					}
				}
				if (found)
					row.style.display = "";
				else
					row.style.display = "none";
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
		Commands <small>Spacecraft Command Database</small>
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

	<div v-if="renderComponent">
		<table id="myTable" class="table table-bordered mb-3 table-striped">
			<thead>
				<tr class="text-center">
					<th class="text-center">Sub-System</th>
					<th class="">Action</th>
					<th class="text-center">TC</th>
					<th class="text-center">TM</th>
				</tr>
			</thead>
			<tbody class="text-body">
				<tr v-if="commands.length > 0" v-for="c in commands">
					<td class="text-center">{{ c.sub }}</td>
					<td class="">{{ c.desc }}</td>
					<td class="text-center text-capitalize">{{ c.tc }}</td>
					<td class="text-center text-capitalize">{{ c.tm }}</td>
				</tr>
			</tbody>
		</table>
	</div>
	<!-- END table -->

</template>