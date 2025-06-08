<script>
import { useAppVariableStore } from '@/stores/app-variable';
import apexchart from '@/components/plugins/Apexcharts.vue';

const appVariable = useAppVariableStore();

export default {
	components: {
		apexchart: apexchart
	},
	data() {
		return {
			renderComponent: true
		}
	},
	methods: {

	},
	mounted() {

	},
	created() {

	}
}
</script>
<template>
	<h1 class="page-header">MCS <small>Monitoring & Control System</small></h1>
	<hr class="mb-4">

	<div class="row" v-if="renderComponent">
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">Telemetry</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Online</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">Position</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Online</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">Ground Stations</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Online</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">Control Queue</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Online</span>
					</div>
				</card-body>
			</card>
		</div>
		
		<h4 class="mt-4">Backend <small>Servers</small></h4>
		<hr class="mb-4">

		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">MQTT</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Connected</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">Database</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Connected</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">API</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Connected</span>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-3 col-lg-6">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-3">
						<span class="flex-grow-1">App</span>
					</div>
					<div class="row align-items-center mb-2 px-5">
						<span class="badge bg-success">Connected</span>
					</div>
				</card-body>
			</card>
		</div>
	</div>

</template>