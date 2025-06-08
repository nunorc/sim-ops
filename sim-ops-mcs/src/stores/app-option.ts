import { defineStore } from "pinia";
import getEnv from '@/utils/env';

export const useAppOptionStore = defineStore({
  id: "appOption",
  state: () => {
    return {
    	appMode: '',
    	appThemeClass: '',
    	appCoverClass: '',
		appBoxedLayout: false,
		appHeaderHide: false,
		appHeaderSearchToggled: false,
		appSidebarCollapsed: false,
		appSidebarMobileToggled: false,
		appSidebarMobileClosed: false,
		appSidebarHide: false,
		appContentFullHeight: false,
		appContentClass: '',
		appTopNav: false,
		appFooter: false,
		appFooterFixed: false,
		soAPI: getEnv('SO_API', '/api'),
		soAuth: false,
		soCompact: false
	}
  }
});
