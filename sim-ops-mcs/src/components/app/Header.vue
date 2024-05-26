<script setup lang="ts">
import { slideToggle } from '@/composables/slideToggle.js';
import { useAppOptionStore } from '@/stores/app-option';
import { RouterLink } from 'vue-router';

const appOption = useAppOptionStore();
const notificationData = [{
	icon: 'bi bi-bag text-theme',
	title: 'NEW ORDER RECEIVED ($1,299)',
	time: 'JUST NOW'
},{
	icon: 'bi bi-person-circle text-theme',
	title: '3 NEW ACCOUNT CREATED',
	time: '2 MINUTES AGO'
},{
	icon: 'bi bi-gear text-theme',
	title: 'SETUP COMPLETED',
	time: '3 MINUTES AGO'
},{
	icon: 'bi bi-grid text-theme',
	title: 'WIDGET INSTALLATION DONE',
	time: '5 MINUTES AGO'
},{
	icon: 'bi bi-credit-card text-theme',
	title: 'PAYMENT METHOD ENABLED',
	time: '10 MINUTES AGO'
}];

function toggleAppSidebarCollapsed() {
	if (!appOption.appSidebarHide) {
		if (appOption.appSidebarCollapsed) {
			appOption.appSidebarToggled = !appOption.appSidebarToggled;
		} else if (appOption.appSidebarToggled) {
			appOption.appSidebarToggled = !appOption.appSidebarToggled;
		}
		appOption.appSidebarCollapsed = !appOption.appSidebarCollapsed;
	}
}
function toggleAppSidebarMobileToggled() {
	if (!(appOption.appTopNav && appOption.appSidebarHide)) {
		appOption.appSidebarMobileToggled = !appOption.appSidebarMobileToggled;
	} else {
		slideToggle(document.querySelector('.app-top-nav'));
		window.scrollTo(0, 0);
	}
}
function toggleAppHeaderSearch(event: any) {
	event.preventDefault();
	
	appOption.appHeaderSearchToggled = !appOption.appHeaderSearchToggled;
}
function checkForm(event: any) {
	event.preventDefault();
	this.$router.push({ path: '/extra/search' })
}
</script>
<template>
	<div id="header" class="app-header">
		<!-- BEGIN desktop-toggler -->
		<div class="desktop-toggler">
			<button type="button" class="menu-toggler" v-on:click="toggleAppSidebarCollapsed">
				<span class="bar"></span>
				<span class="bar"></span>
				<span class="bar"></span>
			</button>
		</div>
		<!-- BEGIN desktop-toggler -->
		
		<!-- BEGIN mobile-toggler -->
		<div class="mobile-toggler">
			<button type="button" class="menu-toggler" v-on:click="toggleAppSidebarMobileToggled">
				<span class="bar"></span>
				<span class="bar"></span>
				<span class="bar"></span>
			</button>
		</div>
		<!-- END mobile-toggler -->
		
		<!-- BEGIN brand -->
		<div class="brand">
			<RouterLink to="/" class="brand-logo">
				<span class="">
					<!-- <span class="brand-img-text text-theme">SCO-</span> -->
				</span>
				<span class="brand-text">MCS</span>
			</RouterLink>
		</div>
		<!-- END brand -->
		
		<!-- BEGIN menu -->
		<div class="menu">
			<span id="dt-now" class="menu-text pe-5"></span>
			<!-- <RouterLink to="/about" class="menu-text d-sm-block d-none w-170px text-secondary" style="text-align: right; padding-right: 32px;">SimOps</RouterLink> -->
		</div>
		<!-- END menu -->

	</div>
</template>
