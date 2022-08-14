ARG ELK_VERSION

FROM docker.elastic.co/logstash/logstash:${ELK_VERSION}

COPY ./jars/ /usr/share/logstash/logstash-core/lib/jars/

# https://www.docker.elastic.co/


# Add your logstash plugins setup here

# Example: RUN logstash-plugin install logstash-filter-json
