<script>
import { useAppVariableStore } from '@/stores/app-variable';
import { useAppOptionStore } from '@/stores/app-option';

const appVariable = useAppVariableStore(),
      appOption = useAppOptionStore();

export default {

}
</script>
<template>
	<h1 class="page-header">SimOps</h1>
	<hr class="mb-4">

	<div class="">
		<p class="lead">Designed and developed by the SimOps team.</p>

		<h5 class="mt-5">The SimOps Team</h5>
		<p class="lead">Nuno Carvalho, Peter Stöferle, Adrian Calleja, Vladimir Zelenevskiy, Rodrigo Laurinovics, Marcin Kovalevskij, Tim Oerther, Frederik Dall'Omo and David Evans</p>
	</div>

</template>

<style>
.app-w-100 { width: 100%; }
.app-w-80 { width: 86px; height: 60px; }
</style>