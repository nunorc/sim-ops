<script>
import Chart from 'chart.js/auto';
import 'chartjs-adapter-moment';

import { useAppVariableStore } from '@/stores/app-variable';

const appVariable = useAppVariableStore();

export default {
	props: ['data', 'type', 'options', 'width', 'height'],
  mounted() {
  	Chart.defaults.font.family = appVariable.font.bodyFontFamily;
		Chart.defaults.font.size = 12;
		Chart.defaults.color = appVariable.color.bodyColor;
		Chart.defaults.borderColor = appVariable.color.borderColor;
		Chart.defaults.plugins.legend.display = false;
		Chart.defaults.plugins.tooltip.padding = { left: 8, right: 12, top: 8, bottom: 8 };
		Chart.defaults.plugins.tooltip.cornerRadius = 8;
		Chart.defaults.plugins.tooltip.titleMarginBottom = 6;
		Chart.defaults.plugins.tooltip.color = appVariable.color.componentBg;
		Chart.defaults.plugins.tooltip.multiKeyBackground = appVariable.color.componentColor;
		Chart.defaults.plugins.tooltip.backgroundColor = appVariable.color.componentColor;
		Chart.defaults.plugins.tooltip.titleFont.family = appVariable.font.bodyFontFamily;
		Chart.defaults.plugins.tooltip.titleFont.weight = appVariable.font.bodyFontWeight;
		Chart.defaults.plugins.tooltip.footerFont.family = appVariable.font.bodyFontFamily;
		Chart.defaults.plugins.tooltip.displayColors = true;
		Chart.defaults.plugins.tooltip.boxPadding = 6;
		Chart.defaults.scale.grid.color = appVariable.color.borderColor;
		Chart.defaults.scale.beginAtZero = true;
		
		new Chart(this.$refs.canvas, {
			type: this.$props.type,
			data: this.$props.data,
			options: this.$props.options
		});
  }
}
</script>

<template>
	<canvas ref="canvas" :height="height" />
</template>