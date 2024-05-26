<script>
import { ref } from 'vue';
import { useAppVariableStore } from '@/stores/app-variable';
import chartjs from '@/components/plugins/Chartjs.vue';
import datepicker from 'vue3-datepicker';
import Masonry from 'masonry-layout';
import moment from 'moment';
import axios from 'axios';

let appVariable = useAppVariableStore();

export default {
	components: {
		chartjs: chartjs
	},
	methods: {
		updateChartsData() {
			axios.get('http://localhost:8000/opssat/telemetry/values').then((response) => {
				let arr = response.data.reverse();
				let labels = [], val1 = [], val2 = [], val3 = [], val4 = [], val5 = [], val6 = [],
				    val1_y = [], val2_y = [], val3_y = [], val4_y = [], val5_y = [], val6_y = [];
				for (var el of arr) {
					labels.push(el.ts);
					val1.push(el.val1);
					val2.push(el.val2);
					val3.push(el.val3);
					val4.push(el.val4);
					val5.push(el.val5);
					val6.push(el.val6);
					val1_y.push(el.val1_y);
					val2_y.push(el.val2_y);
					val3_y.push(el.val3_y);
					val4_y.push(el.val4_y);
					val5_y.push(el.val5_y);
					val6_y.push(el.val6_y);				
				}

				this.chart1.data.labels = labels;
				this.chart1.data.datasets[0].data = val1;
				this.chart1.data.datasets[1].data = val1_y;
				this.chart1.key = labels[0];
				this.chart2.data.labels = labels;
				this.chart2.data.datasets[0].data = val2;
				this.chart2.data.datasets[1].data = val2_y;
				this.chart2.key = labels[0];
				this.chart3.data.labels = labels;
				this.chart3.data.datasets[0].data = val3;
				this.chart3.data.datasets[1].data = val3_y;
				this.chart3.key = labels[0];
				this.chart4.data.labels = labels;
				this.chart4.data.datasets[0].data = val4;
				this.chart4.data.datasets[1].data = val4_y;
				this.chart4.key = labels[0];
				this.chart5.data.labels = labels;
				this.chart5.data.datasets[0].data = val5;
				this.chart5.data.datasets[1].data = val5_y;
				this.chart5.key = labels[0];
				this.chart6.data.labels = labels;
				this.chart6.data.datasets[0].data = val6;
				this.chart6.data.datasets[1].data = val6_y;
				this.chart6.key = labels[0];
			});
		}
	},
	data() {
		return {
			renderComponent: true,
			chart1: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chart2: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chart3: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chart4: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chart5: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chart6: {
				key: '',
				type: 'line',
				data: {
					labels: [],
					datasets: [{
						color: appVariable.color.theme,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.theme,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.theme,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					},{
						color: appVariable.color.gray,
						backgroundColor: 'transparent',
						borderColor: appVariable.color.gray,
						borderWidth: 2,
						pointBackgroundColor: appVariable.color.bodyBg,
						pointBorderWidth: 2,
						pointRadius: 4,
						pointHoverBackgroundColor: appVariable.color.bodyBg,
						pointHoverBorderColor: appVariable.color.gray,
						pointHoverRadius: 6,
						pointHoverBorderWidth: 2,
						data: []
					}],
				}
			},
			chartOptions: {
				scales: {
					x: {
						type: 'timeseries',
						time: {
							unit: 'second',
							format: "HH:mm:ss",
							displayFormats: {
                            	'minute': 'HH:mm',
                            	'hour': 'HH:mm',
								'second': 'HH:mm:ss'
                        	},
						},
						ticks: { font: { size: 8 }}
					},
					y: {
						min: 0,
						max: 1
					}
				}
			},
			mqtt_status: "checking"
		}
	},
	mounted() {
		const msnry = new Masonry('[data-masonry]');
		this.updateChartsData();

		this.mqtt_status = this.$mqtt.status();

		// subscribe to telemtry topic to get updates
		this.$mqtt.subscribe("opssat/telemetry", (message) => {
			let data = JSON.parse(message.toString());

			if (data.update === 'values')
				this.updateChartsData();
		}, false);
	}
}
</script>
<template>
	<!-- BEGIN page-header -->
	<h1 class="page-header">
		Telemetry <small class="float-end">
			<span class="badge bg-dark">API</span>
			<span v-bind:class="{ 'badge': true, 'bg-success': mqtt_status == 'connected', 'bg-danger': mqtt_status != 'connected' }">online</span>
			<span class="badge bg-dark ms-1">MQTT</span>
			<span v-bind:class="{ 'badge': true, 'bg-success': mqtt_status == 'connected', 'bg-danger': mqtt_status != 'connected' }">{{ mqtt_status }}</span>
		</small>
	</h1>
	<hr class="mb-4">
	<!-- END page-header -->

	<div class="row" v-if="renderComponent">
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 1</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart1.data.datasets[0].data[chart1.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 2</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart2.data.datasets[0].data[chart2.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 3</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart3.data.datasets[0].data[chart3.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 4</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart4.data.datasets[0].data[chart4.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 5</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart5.data.datasets[0].data[chart5.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
		<div class="col-xl-2 col-lg-2">
			<card class="mb-3">
				<card-body>
					<div class="d-flex fw-bold small mb-1">
						<span class="flex-grow-1">Sensor 6</span>
						<i class="fa-solid fa-power-off text-theme"></i>
					</div>
					<div class="row align-items-center">
						<div class="text-center">
							<h3 class="mb-0">{{ chart6.data.datasets[0].data[chart6.data.datasets[0].data.length-1] }}</h3>
						</div>
					</div>
				</card-body>
			</card>
		</div>
	</div>
	<!-- END row -->

	<!-- BEGIN row -->
	<div class="row" data-masonry='{"percentPosition": true }' v-if="renderComponent">
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 1</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart1.key" :type="chart1.type" :data="chart1.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
		
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 2</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart2.key" :type="chart2.type" :data="chart2.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
		
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 3</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart3.key" :type="chart3.type" :data="chart3.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
	</div>
	<!-- END row -->

	<!-- BEGIN row -->
	<div class="row" data-masonry='{"percentPosition": true }' v-if="renderComponent">
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 4</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart4.key" :type="chart4.type" :data="chart4.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
		
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 5</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart5.key" :type="chart5.type" :data="chart5.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
		
		<!-- BEGIN col-4 -->
		<div class="col-lg-6 col-xl-4 mb-4">
			<!-- BEGIN card -->
			<card>
				<card-body>
					<!-- title -->
					<div class="d-flex align-items-center mb-2">
						<div class="flex-fill fw-bold fs-16px">Sensor 6</div>
						<span class="text-decoration-none text-inverse text-opacity-50">real-time</span>
					</div>
					<hr class="opacity-3 my-2 mx-n3" />
					
					<!-- chart -->
					<div>
						<div class="chart mb-2" style="height: 150px">
							<chartjs :key="chart6.key" :type="chart6.type" :data="chart6.data" :options="chartOptions" class="w-100" height="150" />
						</div>
					</div>
				</card-body>
			</card>
			<!-- END card -->
		</div>
		<!-- END col-4 -->
	</div>
	<!-- END row -->
</template>