
FROM docker.elastic.co/logstash/logstash:7.10.0

COPY ./jars/ /usr/share/logstash/logstash-core/lib/jars/

COPY ./log_stash_keystore.sh .

USER root

RUN chmod -R 777 log_stash_keystore.sh

RUN "./log_stash_keystore.sh"