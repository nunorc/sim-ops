#!/bin/sh

# handle htpasswd tasks

/usr/bin/htpasswd -c -b /etc/nginx/htpasswd ${SO_MCS_USERNAME:=sim} ${SO_MCS_PASSWORD:=ops}
/usr/bin/htpasswd -b /etc/nginx/htpasswd admin ${SO_MCS_ADMIN_PASSWORD:=admin}

# handle MCS config

JSON_STRING='window.configs = { '
if [[ ! -z "${SO_API}" ]]; then
  JSON_STRING="${JSON_STRING} 'SO_API': '${SO_API}',"
fi
if [[ ! -z "${SO_MQTT}" ]]; then
  JSON_STRING="${JSON_STRING} 'SO_MQTT': '${SO_MQTT}',"
fi
if [[ ! -z "${SO_MQTT_PORT}" ]]; then
  JSON_STRING="${JSON_STRING} 'SO_MQTT_PORT': parseInt('${SO_MQTT_PORT}'),"
fi
if [[ ! -z "${SO_MQTT_PATH}" ]]; then
  JSON_STRING="${JSON_STRING} 'SO_MQTT_PATH': '${SO_MQTT_PATH}',"
fi
if [[ ! -z "${SO_MCS_SIMPLE}" ]]; then
  JSON_STRING="${JSON_STRING} 'SO_MCS_SIMPLE': parseInt('${SO_MCS_SIMPLE}'),"
else
  JSON_STRING="${JSON_STRING} 'SO_MCS_SIMPLE': 0,"
fi
JSON_STRING=$( echo "${JSON_STRING}" | sed 's#,$##' )
JSON_STRING="${JSON_STRING} };"

sed -i "s@// CONFIGURATIONS_PLACEHOLDER@${JSON_STRING}@" /usr/share/nginx/html/index.html
exec "$@"
