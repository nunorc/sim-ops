<script>
import { useAppVariableStore } from '@/stores/app-variable';

const appVariable = useAppVariableStore();

export default {
	components: {
		
	},
	data() {
		return {
			renderComponent: true,
			procedures: [
				{ 'desc': 'Enable U/L Carrier', 'res': 'Ground Station > U/L Carrier' },
				{ 'desc': 'Disable U/L Carrier', 'res': 'Ground Station > U/L Carrier' },
				{ 'desc': 'Enable Program Track', 'res': 'Ground Station > Program Track' },
				{ 'desc': 'Disable Program Track', 'res': 'Ground Station > Program Track' },
				{ 'desc': 'Enable Ranging', 'res': 'Ground Station > Ranging' },
				{ 'desc': 'Disable Ranging', 'res': 'Ground Station > Ranging' },
				{ 'desc': 'Enable Doppler', 'res': 'Ground Station > Doppler' },
				{ 'desc': 'Disable Doppler', 'res': 'Ground Station > Doppler' },
				{ 'desc': 'Sweep', 'res': 'Ground Station > Sweep Done' },
				{ 'desc': 'Enable Fr. Checks', 'res': 'Ground Station > Frame Checks' },
				{ 'desc': 'Disable Fr. Checks', 'res': 'Ground Station > Frame Checks' },
				{ 'desc': 'Set U/L Power level: 30, 40, 50', 'res': 'Ground Station > U/L Power' },
				{ 'desc': 'Set configuration mode: SLBR, SHBR, XLBR, XHBR', 'res': 'Ground Station > mode' },
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
					//td = tr[i].getElementsByTagName("td")[0];
					if (col) {
						txtValue = col.textContent || col.innerText;
						//console.log(txtValue);
						//console.log(txtValue.toUpperCase().indexOf(filter));
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
		Ground Station <small>Actions & Configuration Modes</small>
		<small class="float-end">
			<span class="badge bg-dark">Database</span>
			<span class="badge bg-success">Online</span>
		</small>
	</h1>
	<hr class="mb-4">

	<h4 class="pt-3">Actions</h4>
	<div v-if="renderComponent">
		<table id="myTable" class="table table-bordered mb-3 table-striped">
			<thead>
				<tr class="text-center">
					<th class="">Action</th>
					<th class="text-center">Monitor</th>
				</tr>
			</thead>
			<tbody class="text-body">
				<tr v-if="procedures.length > 0" v-for="p in procedures">
					<td class="">{{ p.desc }}</td>
					<td class="text-center text-capitalize">{{ p.res }}</td>
				</tr>
			</tbody>
		</table>
	</div>

	<h4 class="pt-3">Configuration Modes</h4>
	<div v-if="renderComponent">
		<table id="myTable" class="table table-bordered mb-3 table-striped">
			<thead>
				<tr class="text-center">
					<th class="">Mode</th>
					<th class="text-center">Description</th>
				</tr>
			</thead>
			<tbody class="text-body">
				<tr><td>SLBR</td><td>S band low bitrate</td></tr>
				<tr><td>SHBR</td><td>S band high bitrate</td></tr>
				<tr><td>XLBR</td><td>X band low bitrate</td></tr>
				<tr><td>XHBR</td><td>X band high bitrate</td></tr>
			</tbody>
		</table>
	</div>

</template>
