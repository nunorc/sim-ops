<script>
import VueApexCharts from "vue3-apexcharts";
import { useAppVariableStore } from '@/stores/app-variable';

const appVariable = useAppVariableStore();

export function getApexConfiguration() {
	return {
		title: {
			style: {
				fontSize: '14px',
				fontWeight: '600',
				fontFamily: appVariable.font.bodyFontFamily,
				color: appVariable.color.bodyColor
			}
		},
		legend: {
			fontFamily: appVariable.font.bodyFontFamily,
			labels: { colors: appVariable.color.bodyColor }
		},
		tooltip: {
			style: {
				fontSize: '12px',
				fontFamily: appVariable.font.bodyFontFamily
			}
		},
		grid: { borderColor: appVariable.color.borderColor },
		dataLabels: {
			style: {
				fontSize: '12px',
				fontFamily: appVariable.font.bodyFontFamily,
				fontWeight: '600',
				colors: undefined
			}
		},
		xaxis: {
			axisBorder: {
				show: true,
				color: appVariable.color.borderColor,
				height: 1,
				width: '100%',
				offsetX: 0,
				offsetY: -1
			},
			axisTicks: {
				show: true,
				borderType: 'solid',
				color: appVariable.color.borderColor,
				height: 6,
				offsetX: 0,
				offsetY: 0
			},
			labels: {
				style: {
					colors: appVariable.color.bodyColor,
					fontSize: '12px',
					fontFamily: appVariable.font.bodyFontFamily,
					fontWeight: appVariable.font.bodyFontWeight,
					cssClass: 'apexcharts-xaxis-label',
				}
			}
		},
		yaxis: {
			labels: {
				style: {
					colors: appVariable.color.bodyColor,
					fontSize: '12px',
					fontFamily: appVariable.font.bodyFontFamily,
					fontWeight: appVariable.font.bodyFontWeight,
					cssClass: 'apexcharts-xaxis-label',
				}
			}
		}
	};
}

Apex = getApexConfiguration();

export default {
	props: ['height', 'options', 'series'],
  components: {
    apexchart: VueApexCharts,
  }
};
</script>

<template>
  <div>
    <apexchart
      :height="height"
      :options="options"
      :series="series"
    ></apexchart>
  </div>
</template>