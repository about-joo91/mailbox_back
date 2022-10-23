
FROM docker.elastic.co/logstash/logstash:8.4.3

WORKDIR /app/logstash

COPY logstash/config/logstash.yml /usr/share/logstash/config/logstash.yml

COPY logstash/jars/ /usr/share/logstash/logstash-core/lib/jars/

COPY logstash/log_stash_keystore.sh .

USER root

RUN chmod -R 777 log_stash_keystore.sh

RUN "./log_stash_keystore.sh"