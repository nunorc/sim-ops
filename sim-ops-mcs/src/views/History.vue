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
			renderComponent: true,
			loading: true,
			running: null,
			hist: []
		}
	},
	methods: {
		updateHist() {
			axios.get(`${appOption.soAPI}/admin/hist`)
				.then((resp) => {
					this.loading = false;

					this.hist = resp.data;
				})
		},
		ppDate(ts) {
			let dt = new Date(ts*1000);
			return dt.toISOString().replace('T', ' ').replace('Z','') + ' UTC';
		}
	},
	mounted() {
		this.updateHist();
	}
}
</script>
<template>

	<div id="toasts-container" class="toasts-container" style="z-index: 10;"></div>

	<!-- BEGIN page-header -->
	<h1 class="page-header">
		<span v-if="loading" class="spinner-border text-secondary app-fs-small" role="status"><span class="visually-hidden">Loading...</span></span>
		History <small>TC & Control</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<card v-for="h in hist" class="mb-4" v-if="renderComponent">
		<card-header>{{ (new Date(h[0]*1000)).toString().split("+")[0] }}</card-header>
		<card-body>
			<table class="table table-sm">
			<thead>
				<tr class="">
					<th>Timestamp</th>
					<th>System</th>
					<th>TC/Control</th>
					<th>Result</th>
				</tr>
			</thead>
			<tbody class="text-body">
				<tr v-if="h[1].length > 0" v-for="r in h[1]">
					<td>{{ ppDate(r.ts) }}</td>
					<td>{{ r.system }}</td>
					<td>{{ r.system === 'spacecraft' ? r.command : r.control+': '+r.value }}</td>
					<td v-if="r.system==='ground_station'">
						<span class="fw-bold" :class="{ 'text-theme': r.result==='OK', 'text-danger': r.result!=='OK'}">{{ r.result }}</span>
					</td>
					<td v-if="r.system==='spacecraft'" class="">
						<span v-if="r.result.length>0" class="fw-bold" :class="{ 'text-theme': r.result.split(' ')[0].split(':')[0]==='g', 'text-danger': r.result.split(' ')[0].split(':')[0]==='r'}">{{ r.result.split(' ')[0].split(':')[1] }}</span>&nbsp;
						<span v-if="r.result.length>0" class="fw-bold" :class="{ 'text-theme': r.result.split(' ')[1].split(':')[0]==='g', 'text-danger': r.result.split(' ')[1].split(':')[0]==='r', 'text-warning': r.result.split(' ')[1].split(':')[0]==='w'}">{{ r.result.split(' ')[1].split(':')[1] }}</span>&nbsp;
						<span v-if="r.result.length>0" class="fw-bold" :class="{ 'text-theme': r.result.split(' ')[2].split(':')[0]==='g', 'text-danger': r.result.split(' ')[2].split(':')[0]==='r', 'text-warning': r.result.split(' ')[2].split(':')[0]==='w' }">{{ r.result.split(' ')[2].split(':')[1] }}</span>
					</td>
				</tr>
			</tbody>
		</table>
		</card-body>
	</card>



</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
.app-fs-small { font-size: small; }
</style>