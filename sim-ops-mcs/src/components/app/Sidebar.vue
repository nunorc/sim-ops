<script setup lang="ts">
import { useAppSidebarMenuStore } from '@/stores/app-sidebar-menu';
import { useAppOptionStore } from '@/stores/app-option';
import { onMounted } from 'vue';
import SidebarNav from '@/components/app/SidebarNav.vue';

const appSidebarMenu = useAppSidebarMenuStore();
const appOption = useAppOptionStore();

function appSidebarMobileToggled() {
	appOption.appSidebarMobileToggled = !appOption.appSidebarMobileToggled;
}

onMounted(() => {
	var handleSidebarMenuToggle = function(menus) {
		menus.map(function(menu) {
			menu.onclick = function(e) {
				e.preventDefault();
				var target = this.nextElementSibling;

				menus.map(function(m) {
					var otherTarget = m.nextElementSibling;
					if (otherTarget !== target) {
						otherTarget.style.display = 'none';
						otherTarget.closest('.menu-item').classList.remove('expand');
					}
				});

				var targetItemElm = target.closest('.menu-item');

				if (targetItemElm.classList.contains('expand') || (targetItemElm.classList.contains('active') && !target.style.display)) {
					targetItemElm.classList.remove('expand');
					target.style.display = 'none';
				} else {
					targetItemElm.classList.add('expand');
					target.style.display = 'block';
				}
			}
		});
	};
	
	var menuBaseSelector = '.app-sidebar .menu > .menu-item.has-sub';
	var submenuBaseSelector = ' > .menu-submenu > .menu-item.has-sub';

	// menu
	var menuLinkSelector =  menuBaseSelector + ' > .menu-link';
	var menus = [].slice.call(document.querySelectorAll(menuLinkSelector));
	handleSidebarMenuToggle(menus);

	// submenu lvl 1
	var submenuLvl1Selector = menuBaseSelector + submenuBaseSelector;
	var submenusLvl1 = [].slice.call(document.querySelectorAll(submenuLvl1Selector + ' > .menu-link'));
	handleSidebarMenuToggle(submenusLvl1);

	// submenu lvl 2
	var submenuLvl2Selector = menuBaseSelector + submenuBaseSelector + submenuBaseSelector;
	var submenusLvl2 = [].slice.call(document.querySelectorAll(submenuLvl2Selector + ' > .menu-link'));
	handleSidebarMenuToggle(submenusLvl2);
});
</script>
<template>
	<div id="sidebar" class="app-sidebar">
		<perfect-scrollbar class="app-sidebar-content">
			<div class="menu">
				<template v-for="menu in appSidebarMenu">
					<div class="menu-header" v-if="menu.is_header">{{ menu.text }}</div>
					<div class="menu-divider" v-else-if="menu.is_divider"></div>
					<template v-else>
						<sidebar-nav v-if="menu.text" v-bind:menu="menu"></sidebar-nav>
					</template>
				</template>
			</div>
		</perfect-scrollbar>
	</div>
	<button class="app-sidebar-mobile-backdrop" v-on:click="appSidebarMobileToggled"></button>
</template>