<script>
	export default {
		props: ['target'],
		methods: {
			scrollTo(event) {
				event.preventDefault();
				
				var elm = this.$refs.elm;
				var targetAttr = this.$props.target;
				var targetElm = document.querySelectorAll(targetAttr)[0];
				var targetHeader = document.querySelectorAll('.app-header')[0];
				var targetHeight = targetHeader.offsetHeight;
				if (targetElm) {
					var targetTop = targetElm.offsetTop - targetHeight - 24;
					window.scrollTo({top: targetTop, behavior: 'smooth'});
				}
			}
		}
	}
</script>
<template>
	<a class="nav-link" ref="elm" :href="target" @click="(event) => scrollTo(event)">
		<slot />
	</a>
</template>