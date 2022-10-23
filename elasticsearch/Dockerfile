
FROM docker.elastic.co/elasticsearch/elasticsearch:8.4.3

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu
RUN elasticsearch-plugin install analysis-nori

COPY /elasticsearch/config/elasticsearch.yml .

RUN mv elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml