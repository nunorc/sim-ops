import { defineStore } from "pinia";

export const useAppSidebarMenuStore = defineStore({
    id: "appSidebarMenu",
    state: () => {
        let items = [
            { 'text': 'Telemetry', 'is_header': true},
            { 'url': '/aocs', 'icon': 'bi bi-columns-gap', 'text': 'AOCS' },
            { 'url': '/ttc', 'icon': 'bi bi-columns-gap', 'text': 'TTC' },
            { 'url': '/eps', 'icon': 'bi bi-columns-gap', 'text': 'EPS' },
            { 'url': '/dhs', 'icon': 'bi bi-columns-gap', 'text': 'DHS' },
            { 'url': '/payload', 'icon': 'bi bi-columns-gap', 'text': 'Payload' },
            { 'text': 'Monitoring', 'is_header': true },
            { 'url': '/spacecraft', 'icon': 'fa-solid fa-satellite', 'text': 'Spacecraft' },
            { 'url': '/ground_station', 'icon': 'fa-solid fa-satellite-dish', 'text': 'Ground Station' },
            { 'text': 'Control', 'is_header': true },
            { 'url': '/spacon', 'icon': 'fa-solid fa-satellite', 'text': 'SpaCon' },
            { 'url': '/om', 'icon': 'fa-solid fa-satellite-dish', 'text': 'OM' },
            { 'text': 'Operations', 'is_header': true },
            { 'url': '/commands', 'icon': 'bi bi-list-check', 'text': 'SC Commands' },
            { 'url': '/procedures', 'icon': 'bi bi-list-check', 'text': 'Procedures' },
            { 'url': '/gs_config', 'icon': 'bi bi-list-check', 'text': 'GS Config' },
            { 'text': 'Products', 'is_header': true },
            { 'url': '/flight-dynamics', 'icon': 'far fa-folder', 'text': 'Flight Dynamics'},
            { 'url': '/packet-store', 'icon': 'far fa-folder', 'text': 'Packet Store' },
            { 'text': 'Sim Officer', 'is_header': true },
            { 'url': '/admin', 'icon': 'bi bi-gear', 'text': 'Admin' },
            { 'url': '/history', 'icon': 'fas fa-history', 'text': 'History' },
            { 'url': '/about', 'icon': 'fas fa-info-circle', 'text': 'About'}
        ]

        return items;
    }
});
