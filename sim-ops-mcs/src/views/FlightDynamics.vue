<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';
import jsVectorMap from 'jsvectormap';
import axios from 'axios';

const appVariable = useAppVariableStore(),
      appOption = useAppOptionStore();

export default {
	data() {
		return {
			renderComponent: true,
			data: null,
			loading: false,
			error: null
		};
	},
	mounted() {
		this.fetchData();
	},
	methods: {
		fetchData() {
			this.loading = true;
			
			axios.get(`${appOption.soAPI}/obj-store/fd`)
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
		ppStatus(status) {
			if (status === 0)
				return 'Not Processed'
			if (status === 1)
				return 'Processing'
			if (status === 2)
				return 'Ready'
			if (status === -1)
				return 'Failed'
			return 'Unknown'
		},
		ppValidity(validity) {
			if (validity === 0)
				return 'Bad'
			if (validity === 1)
				return 'Average'
			if (validity === 2)
				return 'Good'
			return 'Unknown'
		},
		updateObject(uid, key, value, event) {
			let button = event.target;
			button.disabled = true;

			axios.get(`${appOption.soAPI}/obj-store/set/${uid}/${key}/${value}`)
				.then((resp) => {
					if (resp.status===200) {
						this.fetchData();
					}
					else {
						button.disabled = false;
						alert("Processing request submission failed.");
					}
				})
		}
	}
}
</script>
<template>
	<h1 class="page-header">Flight Dynamics <small>Products</small></h1>
	<hr class="mb-4">

	<div v-if="renderComponent && loading">
		Loading ...
	</div>

	<div v-if="renderComponent && !loading">
		<card class="mb-3" v-for="d in data">
			<card-header class="fw-bold">PASS {{ d.id }}</card-header>
			<card-body class="mb-1">
				<div class="row">
					<div class="col-xl-2 col-lg-2">
						<p>Status<br/>
						<span style="width: 120px;" class="badge rounded-0 text-uppercase small" :class="{ 'text-bg-danger': d.status<=0, 'text-bg-warning': d.status===1, 'text-bg-theme': d.status===2 }">{{ ppStatus(d.status) }}</span></p>
						<p>Actions<br/>
						<button @click="updateObject(d.id, 'status', 1, $event)" type="button" class="btn btn-sm btn-outline-theme" :disabled="d.status != 0">Request Processing</button></p>
					</div>
					<div class="col-xl-10 col-lg-10">
						<div class="form-group table-responsive" style="max-height: 200px;">
							<label class="form-label">Data</label>
							<table class="table table-sm small">
								<thead>
									<tr>
										<td>P<sub>x</sub></td><td>P<sub>y</sub></td><td>P<sub>z</sub></td><td>Range</td><td>Doppler</td>
									</tr>
								</thead>
								<tbody>
									<tr v-for="row in d.data">
										<td v-for="col in row.slice(0, 5)" class="small">{{ col }}</td>
									</tr>
								</tbody>
							</table>
						</div>
					</div>
				</div>
			</card-body>
		</card>
		<p v-if="data && data.length === 0">No products found.</p>
	</div>

</template>
