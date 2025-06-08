<script>
import { useAppVariableStore } from '@/stores/app-variable';

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
				{ 'sub': 'AOCS', 'desc': 'Calibrate AOCS sensors', 'tc': 'TC_AOCS_021', 'tm': 'AOCS > AOCS Valid' },

				{ 'sub': 'TTC', 'desc': 'Set TTC mode S_Sup_LBR (hp)', 'tc': 'TC_TTC_001', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode S_Sup_HBR (hp)' , 'tc': 'TC_TTC_002', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode X_Sup_LBR (hp)', 'tc': 'TC_TTC_003', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode X_Sup_HBR (hp)', 'tc': 'TC_TTC_004', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode S_Res_LBR (hp)', 'tc': 'TC_TTC_005', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode X_Res_LBR (hp)' , 'tc': 'TC_TTC_006', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode S_Sub_LBR (hp)', 'tc': 'TC_TTC_007', 'tm': 'TTC > TTC Mode' },
				{ 'sub': 'TTC', 'desc': 'Set TTC mode X_Sub_LBR (hp)', 'tc': 'TC_TTC_008', 'tm': 'TTC > TTC Mode' },

				{ 'sub': 'TTC', 'desc': 'Set TTC chain A', 'tc': 'TC_TTC_011', 'tm': 'TTC > TTC Chain' },
				{ 'sub': 'TTC', 'desc': 'Set TTC chain B', 'tc': 'TC_TTC_012', 'tm': 'TTC > TTC Chain' },
				{ 'sub': 'TTC', 'desc': 'Ping spacecraft', 'tc': 'TC_TTC_021', 'tm': 'TTC > TTC Pink Ack' },
				{ 'sub': 'TTC', 'desc': 'Enable coherent transponder (hp)', 'tc': 'TC_TTC_022', 'tm': 'TTC > Coherent' },
				{ 'sub': 'TTC', 'desc': 'Disable coherent transponder (hp)', 'tc': 'TC_TTC_023', 'tm': 'TTC > Coherent' },
				{ 'sub': 'TTC', 'desc': 'Set Transmitter ON (hp)', 'tc': 'TC_TTC_031', 'tm': 'TTC > TTC TX status' },
				{ 'sub': 'TTC', 'desc': 'Set Transmitter OFF (hp)', 'tc': 'TC_TTC_032', 'tm': 'TTC > TTC TX status' },
				{ 'sub': 'TTC', 'desc': 'Reboot OBC (hp)', 'tc': 'TC_TTC_041', 'tm': 'TTC > OBC Status' },
				{ 'sub': 'TTC', 'desc': 'Set TTC Sb antenna to LGA RHC (hp)', 'tc': 'TC_TTC_051', 'tm': 'TTC > TTC Antenna' },
				{ 'sub': 'TTC', 'desc': 'Set TTC Sb antenna to LGA LHC (hp)', 'tc': 'TC_TTC_052', 'tm': 'TTC > TTC Antenna' },
				{ 'sub': 'TTC', 'desc': 'Set TTC Xb antenna to MGA (hp)', 'tc': 'TC_TTC_053', 'tm': 'TTC > TTC Antenna' },
				{ 'sub': 'TTC', 'desc': 'Set TTC Xb antenna to HGA (hp)', 'tc': 'TC_TTC_054', 'tm': 'TTC > TTC Antenna' },
				{ 'sub': 'TTC', 'desc': 'Enable ranging (hp)', 'tc': 'TC_TTC_061', 'tm': 'TTC > Ranging' },
				{ 'sub': 'TTC', 'desc': 'Disable ranging (hp)', 'tc': 'TC_TTC_062', 'tm': 'TTC > Ranging' },

				{ 'sub': 'EPS', 'desc': 'Set EPS chain A', 'tc': 'TC_EPS_001', 'tm': 'EPS > EPS Chain' },
				{ 'sub': 'EPS', 'desc': 'Set EPS chain B', 'tc': 'TC_EPS_002', 'tm': 'EPS > EPS Chain' },
				{ 'sub': 'EPS', 'desc': 'Enable solar Array 1', 'tc': 'TC_EPS_011', 'tm': 'EPS > Solar Array 1' },
				{ 'sub': 'EPS', 'desc': 'Disable solar Array 1', 'tc': 'TC_EPS_012', 'tm': 'EPS > Solar Array 1' },
				{ 'sub': 'EPS', 'desc': 'Enable solar Array 2', 'tc': 'TC_EPS_021', 'tm': 'EPS > Solar Array 2' },
				{ 'sub': 'EPS', 'desc': 'Disable solar Array 2', 'tc': 'TC_EPS_022', 'tm': 'EPS > Solar Array 2' },

				{ 'sub': 'DHS', 'desc': 'Set DHS chain A', 'tc': 'TC_DHS_001', 'tm': 'DHS > DHS Chain' },
				{ 'sub': 'DHS', 'desc': 'Set DHS chain B', 'tc': 'TC_DHS_002', 'tm': 'DHS > DHS Chain' },
				{ 'sub': 'DHS', 'desc': 'Set OBSW to safe mode', 'tc': 'TC_DHS_011', 'tm': 'DHS > OBSW Mode' },
				{ 'sub': 'DHS', 'desc': 'Set OBSW to nominal mode', 'tc': 'TC_DHS_012', 'tm': 'DHS > OBSW Mode' },
				{ 'sub': 'DHS', 'desc': 'Enable memory downlink dump', 'tc': 'TC_DHS_021', 'tm': 'DHS > Memory Dump' },
				{ 'sub': 'DHS', 'desc': 'Disable memory downlink dump', 'tc': 'TC_DHS_022', 'tm': 'DHS > Memory Dump' },

				{ 'sub': 'Payload', 'desc': 'Power on GPS receiver (nm)', 'tc': 'TC_PL_001', 'tm': 'Payload > GPS Status' },
				{ 'sub': 'Payload', 'desc': 'Power off GPS receiver (nm)', 'tc': 'TC_PL_002', 'tm': 'Payload > GPS Status' },
				{ 'sub': 'Payload', 'desc': 'Power on camera (nm)', 'tc': 'TC_PL_011', 'tm': 'Payload > Camera Status' },
				{ 'sub': 'Payload', 'desc': 'Power off camera (nm)', 'tc': 'TC_PL_012', 'tm': 'Payload > Camera Status' },
				{ 'sub': 'Payload', 'desc': 'Power on SDR (nm)', 'tc': 'TC_PL_021', 'tm': 'Payload > SDR Status' },
				{ 'sub': 'Payload', 'desc': 'Power off SDR (nm)', 'tc': 'TC_PL_022', 'tm': 'Payload > SDR Status' }
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
	<h1 class="page-header">
		Commands <small>Spacecraft Commands Database</small>
		<small class="float-end">
			<span class="badge bg-dark">Database</span>
			<span class="badge bg-success">Online</span>
		</small>
	</h1>
	<hr class="mb-4">

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
		<p>
			(hp) high priority command<br/>(nm) requires OBSW Mode nominal
		</p>
	</div>

</template>