<script>
import { Tooltip } from 'bootstrap';

export default {
	mounted() {
		// expand
		this.$refs.toggler.onclick = function(e) {
			e.preventDefault();
			
			var target = this.closest('.card');
			var targetClass = 'card-expand';
			var targetTop = 40;

			if (document.body.classList.contains(targetClass) && target.classList.contains(targetClass)) {
				target.removeAttribute('style');
				target.classList.remove(targetClass);
				document.body.classList.remove(targetClass);
			} else {
				document.body.classList.add(targetClass);
				target.classList.add(targetClass);
			}

			window.dispatchEvent(new Event('resize'));
		};
		
		new Tooltip(this.$refs.toggler, {
			title: 'Expand / Compress',
			placement: 'bottom',
			trigger: 'hover',
			container: 'body'
		});
	}
}
</script>
<template>
	<a href="#" data-toggle="card-expand" ref="toggler" class="text-white text-opacity-50 text-decoration-none"><i class="bi bi-fullscreen"></i></a>
</template>
