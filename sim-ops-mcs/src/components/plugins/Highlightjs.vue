<script>
import 'highlight.js/lib/common';
import hljsVuePlugin from "@highlightjs/vue-plugin";

export default {
	props: ['code'],
	components: {
		highlightjs: hljsVuePlugin.component
	}
}
</script>

<template>
	<div class="hljs-container">
  	<highlightjs autodetect :code="code" />
  </div>
</template>