ARG ELK_VERSION

FROM docker.elastic.co/logstash/logstash:${ELK_VERSION}

COPY ./jars/ /usr/share/logstash/logstash-core/lib/jars/

COPY ./log_stash_keystore.sh .

USER root

RUN chmod -R 777 log_stash_keystore.sh

RUN "./log_stash_keystore.sh" 