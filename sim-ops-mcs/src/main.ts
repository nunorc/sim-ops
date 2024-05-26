import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { Vue3ProgressPlugin } from '@marcoschulte/vue3-progress';
import PerfectScrollbar from 'vue3-perfect-scrollbar';
import mitt from 'mitt';
import 'vue3-perfect-scrollbar/dist/vue3-perfect-scrollbar.css';
import '@marcoschulte/vue3-progress/dist/index.css';
import '@fortawesome/fontawesome-free/scss/fontawesome.scss';
import '@fortawesome/fontawesome-free/scss/regular.scss';
import '@fortawesome/fontawesome-free/scss/solid.scss';
import '@fortawesome/fontawesome-free/scss/brands.scss';
import '@fortawesome/fontawesome-free/scss/v4-shims.scss';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap';
import './scss/styles.scss';

import App from './App.vue';
import router from './router';

import Card from '@/components/bootstrap/Card.vue';
import CardBody from '@/components/bootstrap/CardBody.vue';
import CardHeader from '@/components/bootstrap/CardHeader.vue';
import CardFooter from '@/components/bootstrap/CardFooter.vue';
import CardGroup from '@/components/bootstrap/CardGroup.vue';
import CardImgOverlay from '@/components/bootstrap/CardImgOverlay.vue';
import CardExpandToggler from '@/components/bootstrap/CardExpandToggler.vue';

import { createPahoMqttPlugin } from 'vue-paho-mqtt';

import getEnv from '@/utils/env';

const emitter = mitt();
const app = createApp(App);

app.component('Card', Card);
app.component('CardBody', CardBody);
app.component('CardHeader', CardHeader);
app.component('CardFooter', CardFooter);
app.component('CardGroup', CardGroup);
app.component('CardImgOverlay', CardImgOverlay);
app.component('CardExpandToggler', CardExpandToggler);

app.use(createPinia());
app.use(router);
app.use(Vue3ProgressPlugin);
app.use(PerfectScrollbar);

app.use(createPahoMqttPlugin({
      PluginOptions: {
        autoConnect: true,
        showNotifications: false,
      },
      MqttOptions: {
        host: getEnv('SO_MQTT', window.location.hostname),
        port: parseInt(getEnv('SO_MQTT_PORT', window.location.port)),
        mainTopic: getEnv('SQ_MQTT_PATH', '/mqtt'),
        clientId: `MyID-${Math.random() * 9999}`
      },
    }));
app.config.globalProperties.emitter = emitter;
app.mount('#app');
