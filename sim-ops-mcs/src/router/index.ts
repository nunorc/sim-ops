import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
	{ path: '/', component: () => import('../views/Dashboard.vue') },
	// telemetry
	{ path: '/aocs', component: () => import('../views/AOCS.vue') },
	{ path: '/ttc', component: () => import('../views/TTC.vue') },
	{ path: '/pts', component: () => import('../views/PTS.vue') },
	{ path: '/dhs', component: () => import('../views/DHS.vue') },
	{ path: '/payload', component: () => import('../views/Payload.vue') },
	// monitoring
	{ path: '/spacecraft', component: () => import('../views/Spacecraft.vue') },
	{ path: '/ground_station', component: () => import('../views/GroundStation.vue') },
	// control
	{ path: '/spacon', component: () => import('../views/SpaCon.vue') },
	{ path: '/om', component: () => import('../views/OM.vue') },
	// procedures
	{ path: '/commands', component: () => import('../views/Commands.vue') },
	{ path: '/procedures', component: () => import('../views/Procedures.vue') },
	{ path: '/gs_config', component: () => import('../views/GSConfig.vue') },
	// admin
	{ path: '/admin', component: () => import('../views/Admin.vue') },
	{ path: '/history', component: () => import('../views/History.vue') },
	// other
	{ path: '/about', component: () => import('../views/About.vue') },
	{ path: '/:pathMatch(.*)*', component: () => import('../views/PageError.vue') }
  ],
});

export default router;
