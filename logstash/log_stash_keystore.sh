#!/bin/sh
echo "=== CREATE Keystore ==="
if [ -f /usr/share/logstash/config/logstash.keystore ]; then
    echo "Remove old logstash.keystore"
    rm /usr/share/logstash/config/logstash.keystore
fi
echo "y" | /usr/share/logstash/bin/logstash-keystore create
echo "$MONGLE_HOST" | /usr/share/logstash/bin/logstash-keystore add 'MONGLE_HOST' -x
echo "$MONGLE_PORT" | /usr/share/logstash/bin/logstash-keystore add 'MONGLE_PORT' -x
echo "$MONGLE_PASSWORD" | /usr/share/logstash/bin/logstash-keystore add 'MONGLE_PASSWORD' -x
echo "$MONGLE_USER" | /usr/share/logstash/bin/logstash-keystore add 'MONGLE_USER' -x
echo "$MONGLE_DB_NAME" | /usr/share/logstash/bin/logstash-keystore add 'MONGLE_DB_NAME' -x

exec "$@"