<script>
import { useAppOptionStore } from '@/stores/app-option';
import { RouterLink } from 'vue-router';

const appOption = useAppOptionStore();

export default {
	mounted() {
		appOption.appSidebarHide = true;
		appOption.appHeaderHide = true;
		appOption.appContentClass = 'p-0';
	},
	beforeUnmount() {
		appOption.appSidebarHide = false;
		appOption.appHeaderHide = false;
		appOption.appContentClass = '';
	}
}
</script>
<template>
	<!-- BEGIN error -->
	<div class="error-page">
		<!-- BEGIN error-page-content -->
		<div class="error-page-content">
			<card class="mb-5 mx-auto" style="max-width: 320px;">
				<card-body>
					<card>
						<div class="error-code">404</div>
					</card>
				</card-body>
			</card>
			<h1>Oops!</h1> 
			<h3>We can't seem to find the page you're looking for</h3>
			<hr />
			<a href="javascript:window.history.back();" class="btn btn-outline-theme px-3 rounded-pill"><i class="fa fa-arrow-left me-1 ms-n1"></i> Go Back</a>
		</div>
		<!-- END error-page-content -->
	</div>
	<!-- END error -->
</template>