<script setup lang="ts">
import { useAppOptionStore } from '@/stores/app-option';
import { useAppVariableStore, generateVariables } from '@/stores/app-variable';
import { onMounted } from 'vue';
import { Tooltip } from 'bootstrap';
import useEmitter from '@/composables/useEmitter';

const appOption = useAppOptionStore();
const appVariable = useAppVariableStore();
const emitter = useEmitter();

var modeList = [
 { name: 'Dark', img: '/assets/img/mode/dark.jpg', value: 'dark' },
 { name: 'Light', img: '/assets/img/mode/light.jpg', value: 'light' },
];

var themeList = [
 { name: 'Pink', bgClass: 'bg-pink', themeClass: 'theme-pink' },
 { name: 'Red', bgClass: 'bg-red', themeClass: 'theme-red' },
 { name: 'Orange', bgClass: 'bg-warning', themeClass: 'theme-warning' },
 { name: 'Yellow', bgClass: 'bg-yellow', themeClass: 'theme-yellow' },
 { name: 'Lime', bgClass: 'bg-lime', themeClass: 'theme-lime' },
 { name: 'Green', bgClass: 'bg-green', themeClass: 'theme-green' },
 { name: 'Default', bgClass: 'bg-teal', themeClass: 'theme-teal' },
 { name: 'Cyan', bgClass: 'bg-info', themeClass: 'theme-info' },
 { name: 'Blue', bgClass: 'bg-primary', themeClass: 'theme-primary' },
 { name: 'Purple', bgClass: 'bg-purple', themeClass: 'theme-purple' },
 { name: 'Indigo', bgClass: 'bg-indigo', themeClass: 'theme-indigo' },
 { name: 'Gray', bgClass: 'bg-gray-200', themeClass: 'theme-gray-200' }
];

var coverList = [
	{ name: 'Default', coverThumbImage: '/assets/img/cover/cover-thumb-1.jpg', coverClass: 'bg-cover-1'},
	{ name: 'Cover 2', coverThumbImage: '/assets/img/cover/cover-thumb-2.jpg', coverClass: 'bg-cover-2'},
	{ name: 'Cover 3', coverThumbImage: '/assets/img/cover/cover-thumb-3.jpg', coverClass: 'bg-cover-3'},
	{ name: 'Cover 4', coverThumbImage: '/assets/img/cover/cover-thumb-4.jpg', coverClass: 'bg-cover-4'},
	{ name: 'Cover 5', coverThumbImage: '/assets/img/cover/cover-thumb-5.jpg', coverClass: 'bg-cover-5'},
	{ name: 'Cover 6', coverThumbImage: '/assets/img/cover/cover-thumb-6.jpg', coverClass: 'bg-cover-6'},
	{ name: 'Cover 7', coverThumbImage: '/assets/img/cover/cover-thumb-7.jpg', coverClass: 'bg-cover-7'},
	{ name: 'Cover 8', coverThumbImage: '/assets/img/cover/cover-thumb-8.jpg', coverClass: 'bg-cover-8'},
	{ name: 'Cover 9', coverThumbImage: '/assets/img/cover/cover-thumb-9.jpg', coverClass: 'bg-cover-9'}
]

function appThemePanelToggled(event) {
	event.preventDefault();
	
	appOption.appThemePanelToggled = !appOption.appThemePanelToggled;
	
	if (localStorage) {
		localStorage.appThemePanelToggled = appOption.appThemePanelToggled;
	}
}

function reloadVariable() {
	var newVariables = generateVariables();
	appVariable.font = newVariables.font;
	appVariable.color = newVariables.color;
}

function toggleTheme(event, themeClass) {
	event.preventDefault();
	
	appOption.appThemeClass = themeClass;
	
	if (localStorage) {
		localStorage.appThemeClass = appOption.appThemeClass;
	}
	setThemeClass(localStorage.appThemeClass);
}

function toggleCover(event, coverClass) {
	event.preventDefault();
	
	appOption.appCoverClass = coverClass;
	
	if (localStorage) {
		localStorage.appCoverClass = appOption.appCoverClass;
	}
	setCoverClass(appOption.appCoverClass);
}

function setCoverClass(coverClass) {
	var htmlElm = document.querySelector('html');
	for (var x = 0; x < document.documentElement.classList.length; x++) {
		var targetClass = document.documentElement.classList[x];
		if (targetClass.search('bg-cover-') > -1) {
			htmlElm.classList.remove(targetClass);
		}
	}
	htmlElm.classList.add(coverClass);
}

function toggleMode(event, mode) {
	event.preventDefault();
	
	appOption.appMode = mode;
	
	if (localStorage) {
		localStorage.appMode = appOption.appMode;
	}
	
	setMode(mode);
}

function setMode(mode) {
	document.documentElement.setAttribute('data-bs-theme', mode);
	emitter.emit('theme-reload', true);
	reloadVariable();
}

function setThemeClass(themeClass) {
	for (var x = 0; x < document.body.classList.length; x++) {
		var targetClass = document.body.classList[x];
		if (targetClass.search('theme-') > -1) {
			document.body.classList.remove(targetClass);
		}
	}
	
	document.body.classList.add(themeClass);
	emitter.emit('theme-reload', true);
	reloadVariable();
}

onMounted(() => {
	var elm = document.querySelectorAll('[data-bs-toggle="tooltip"]');
	
	for (var i = 0; i < elm.length; i++) {
		new Tooltip(elm[i]);
	}
	
	if (localStorage) {
		if (localStorage.appThemePanelToggled) {
			appOption.appThemePanelToggled = JSON.parse(localStorage.appThemePanelToggled);
		}
		if (localStorage.appThemeClass) {
			appOption.appThemeClass = localStorage.appThemeClass;
			setThemeClass(localStorage.appThemeClass);
		}
		if (localStorage.appCoverClass) {
			appOption.appCoverClass = localStorage.appCoverClass;
			setCoverClass(appOption.appCoverClass);
		}
		if (localStorage.appMode) {
			appOption.appMode = localStorage.appMode;
			setMode(appOption.appMode);
		}
	}
});

</script>
<template>
	<div class="app-theme-panel" v-bind:class="{ 'active': appOption.appThemePanelToggled }">
			<div class="app-theme-panel-container">
				<a href="#" v-on:click="appThemePanelToggled" class="app-theme-toggle-btn"><i class="bi bi-sliders"></i></a>
				<div class="app-theme-panel-content">
					<div class="small fw-bold text-inverse mb-1">Display Mode</div>
					<card class="card mb-3">
						<card-body class="p-2">
							<div class="row gx-2">
								<div class="col-6" v-for="mode in modeList">
									<a href="javascript:;" 
										v-bind:class="{ 'active': appOption.appMode == mode.value}"
										v-on:click="(event) => toggleMode(event, mode.value)"
										class="app-theme-mode-link">
										<div class="img"><img v-bind:src="mode.img" class="object-fit-cover" height="76" width="76" v-bind:alt="mode.name"></div>
										<div class="text">{{mode.name}}</div>
									</a>
								</div>
							</div>
						</card-body>
					</card>
					<div class="small fw-bold text-inverse mb-1">Theme Color</div>
					<card class="mb-3">
						<card-body class="p-2">
							<div class="app-theme-list">
								<div class="app-theme-list-item" 
									v-bind:class="{ 'active': appOption.appThemeClass == theme.themeClass || (!appOption.appThemeClass && theme.name == 'Default') }" 
									v-for="theme in themeList">
									<a href="javascript:;" class="app-theme-list-link"
										v-bind:class="theme.bgClass"
										v-on:click="(event) => toggleTheme(event, theme.themeClass)"
										data-bs-toggle="tooltip" 
										data-bs-trigger="hover" 
										data-bs-container="body" 
										v-bind:data-bs-title="theme.name">&nbsp;</a>
								</div>
							</div>
						</card-body>
					</card>
					
					<div class="small fw-bold text-inverse mb-1">Theme Cover</div>
					<card>
						<card-body class="p-2">
							<div class="app-theme-cover">
								<div class="app-theme-cover-item" 
									v-bind:class="{ 'active': appOption.appCoverClass == cover.coverClass || (!appOption.appCoverClass && cover.name == 'Default') }" 
									v-for="cover in coverList">
									<a href="javascript:;" class="app-theme-cover-link" 
										v-bind:style="{ backgroundImage: 'url('+ cover.coverThumbImage + ')' }"
										v-on:click="(event) => toggleCover(event, cover.coverClass)"
										data-bs-toggle="tooltip" 
										data-bs-trigger="hover" 
										data-bs-container="body" 
										v-bind:data-bs-title="cover.name">&nbsp;</a>
								</div>
							</div>
						</card-body>
					</card>
				</div>
			</div>
		</div>
</template>
