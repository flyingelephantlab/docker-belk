# Docker BELK stack

This fork is meant to be used with KIPP, having the filebeat running on KIPP maching and the ELK stack on Docker or otherwise running on a different machine/cluster.

TODO: Need to clean up the rest of this README below.

To run filebeat on kipp-vagrant:

    sudo filebeat -e --strict.perms=false -c /apps/kipp/kipp/beats/config/filebeat.yml


Project forked from [docker-elk](https://github.com/deviantony/docker-elk).

Run the latest version of the BELK (Elasticsearch, Logstash, Kibana, Beats) stack with Docker and Docker Compose.

It will give you the ability to analyze any data set by using the searching/aggregation capabilities of Elasticsearch
and the visualization power of Kibana.

Based on the official Docker images:

* [elasticsearch](https://github.com/elastic/elasticsearch-docker)
* [logstash](https://github.com/elastic/logstash-docker)
* [kibana](https://github.com/elastic/kibana-docker)
* [filebeat](https://github.com/elastic/beats-docker)


## Contents

1. [Requirements](#requirements)
   * [Host setup](#host-setup)
   * [SELinux](#selinux)
2. [Getting started](#getting-started)
   * [Bringing up the stack](#bringing-up-the-stack)
   * [Initial setup](#initial-setup)
3. [Configuration](#configuration)
   * [How can I tune the Kibana configuration?](#how-can-i-tune-the-kibana-configuration)
   * [How can I tune the Logstash configuration?](#how-can-i-tune-the-logstash-configuration)
   * [How can I tune the Elasticsearch configuration?](#how-can-i-tune-the-elasticsearch-configuration)
   * [How can I scale out the Elasticsearch cluster?](#how-can-i-scale-up-the-elasticsearch-cluster)
   * [How can I tune the Beats configuration?](#how-can-i-tune-the-beats-configuration)
4. [Storage](#storage)
   * [How can I persist Elasticsearch data?](#how-can-i-persist-elasticsearch-data)
5. [Extensibility](#extensibility)
   * [How can I add plugins?](#how-can-i-add-plugins)
6. [JVM tuning](#jvm-tuning)
   * [How can I specify the amount of memory used by a service?](#how-can-i-specify-the-amount-of-memory-used-by-a-service)
   * [How can I enable a remote JMX connection to a service?](#how-can-i-enable-a-remote-jmx-connection-to-a-service)
7. [E2E debugging](#e2e-debugging)

## Requirements

### Host setup

1. Install [Docker](https://www.docker.com/community-edition#/download) version **1.10.0+**
2. Install [Docker Compose](https://docs.docker.com/compose/install/) version **1.6.0+**
3. Clone this repository

### SELinux

On distributions which have SELinux enabled out-of-the-box you will need to either re-context the files or set SELinux
into Permissive mode in order for docker-belk to start properly. For example on Redhat and CentOS, the following will
apply the proper context:

```bash
$ chcon -R system_u:object_r:admin_home_t:s0 docker-belk/
```

## Usage

### Bringing up the stack

Start the BELK stack using `docker-compose`:

```bash
$ docker-compose up
```

You can also choose to run it in background (detached mode):

```bash
$ docker-compose up -d
```

Give Kibana about 2 minutes to initialize, then access the Kibana web UI by hitting
[http://localhost:5601](http://localhost:5601) with a web browser.

By default, the stack exposes the following ports:
* 5000: Logstash TCP input.
* 9200: Elasticsearch HTTP
* 9300: Elasticsearch TCP transport
* 5601: Kibana

**WARNING**: If you're using `boot2docker`, you must access it via the `boot2docker` IP address instead of `localhost`.

**WARNING**: If you're using *Docker Toolbox*, you must access it via the `docker-machine` IP address instead of
`localhost`.

Now that the stack is running, you will want to inject some log entries. The shipped Logstash configuration allows you
to send content via TCP:

```bash
$ nc localhost 5000 < /path/to/logfile.log
```

## Initial setup

### Default Kibana index pattern creation

When Kibana launches for the first time, it is not configured with any index pattern.

#### Via the Kibana web UI

**NOTE**: You need to inject data into Logstash before being able to configure a Logstash index pattern via the Kibana web
UI. Then all you have to do is hit the *Create* button.

Refer to [Connect Kibana with
Elasticsearch](https://www.elastic.co/guide/en/kibana/current/connect-to-elasticsearch.html) for detailed instructions
about the index pattern configuration.

#### On the command line

Run this command to create a Logstash index pattern:

```bash
$ curl -XPUT -D- 'http://localhost:9200/.kibana/index-pattern/logstash-*' \
    -H 'Content-Type: application/json' \
    -d '{"title" : "logstash-*", "timeFieldName": "@timestamp", "notExpandable": true}'
```

This command will mark the Logstash index pattern as the default index pattern:

```bash
$ curl -XPUT -D- 'http://localhost:9200/.kibana/config/5.5.0' \
    -H 'Content-Type: application/json' \
    -d '{"defaultIndex": "logstash-*"}'
```

## Configuration

**NOTE**: Configuration is not dynamically reloaded, you will need to restart the stack after any change in the
configuration of a component.

### How can I tune the Kibana configuration?

The Kibana default configuration is stored in `kibana/config/kibana.yml`.

It is also possible to map the entire `config` directory instead of a single file.

### How can I tune the Logstash configuration?

The Logstash configuration is stored in `logstash/config/logstash.yml`.

It is also possible to map the entire `config` directory instead of a single file, however you must be aware that
Logstash will be expecting a
[`log4j2.properties`](https://github.com/elastic/logstash-docker/tree/master/build/logstash/config) file for its own
logging.

### How can I tune the Elasticsearch configuration?

The Elasticsearch configuration is stored in `elasticsearch/config/elasticsearch.yml`.

You can also specify the options you want to override directly via environment variables:

```yml
elasticsearch:

  environment:
    network.host: "_non_loopback_"
    cluster.name: "my-cluster"
```

### How can I tune the Beats configuration?

TODO

### How can I scale out the Elasticsearch cluster?

Follow the instructions from the Wiki: [Scaling out
Elasticsearch](https://github.com/deviantony/docker-elk/wiki/Elasticsearch-cluster)

## Storage

### How can I persist Elasticsearch data?

The data stored in Elasticsearch will be persisted after container reboot but not after container removal.

In order to persist Elasticsearch data even after removing the Elasticsearch container, you'll have to mount a volume on
your Docker host. Update the `elasticsearch` service declaration to:

```yml
elasticsearch:

  volumes:
    - /path/to/storage:/usr/share/elasticsearch/data
```

This will store Elasticsearch data inside `/path/to/storage`.

**NOTE:** beware of these OS-specific considerations:
* **Linux:** the [unprivileged `elasticsearch` user][esuser] is used within the Elasticsearch image, therefore the
  mounted data directory must be owned by the uid `1000`.
* **macOS:** the default Docker for Mac configuration allows mounting files from `/Users/`, `/Volumes/`, `/private/`,
  and `/tmp` exclusively. Follow the instructions from the [documentation][macmounts] to add more locations.

[esuser]: https://github.com/elastic/elasticsearch-docker/blob/016bcc9db1dd97ecd0ff60c1290e7fa9142f8ddd/templates/Dockerfile.j2#L22
[macmounts]: https://docs.docker.com/docker-for-mac/osxfs/

## Extensibility

### How can I add plugins?

To add plugins to any BELK component you have to:

1. Add a `RUN` statement to the corresponding `Dockerfile` (eg. `RUN logstash-plugin install logstash-filter-json`)
2. Add the associated plugin code configuration to the service configuration (eg. Logstash input/output)
3. Rebuild the images using the `docker-compose build` command

## JVM tuning

### How can I specify the amount of memory used by a service?

By default, both Elasticsearch and Logstash start with [1/4 of the total host
memory](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/parallel.html#default_heap_size) allocated to
the JVM Heap Size.

The startup scripts for Elasticsearch and Logstash can append extra JVM options from the value of an environment
variable, allowing the user to adjust the amount of memory that can be used by each component:

| Service       | Environment variable |
|---------------|----------------------|
| Elasticsearch | ES_JAVA_OPTS         |
| Logstash      | LS_JAVA_OPTS         |

To accomodate environments where memory is scarce (Docker for Mac has only 2 GB available by default), the Heap Size
allocation is capped by default to 256MB per service in the `docker-compose.yml` file. If you want to override the
default JVM configuration, edit the matching environment variable(s) in the `docker-compose.yml` file.

For example, to increase the maximum JVM Heap Size for Logstash:

```yml
logstash:

  environment:
    LS_JAVA_OPTS: "-Xmx1g -Xms1g"
```

### How can I enable a remote JMX connection to a service?

As for the Java Heap memory (see above), you can specify JVM options to enable JMX and map the JMX port on the docker
host.

Update the `{ES,LS}_JAVA_OPTS` environment variable with the following content (I've mapped the JMX service on the port
18080, you can change that). Do not forget to update the `-Djava.rmi.server.hostname` option with the IP address of your
Docker host (replace **DOCKER_HOST_IP**):

```yml
logstash:

  environment:
    LS_JAVA_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.port=18080 -Dcom.sun.management.jmxremote.rmi.port=18080 -Djava.rmi.server.hostname=DOCKER_HOST_IP -Dcom.sun.management.jmxremote.local.only=false"
```

## E2E debugging

Once we have all the containers up and running we can use the following commands to do various checks:

Creates logs on the filebeat container:
```sh
docker exec -it dockerbelk_filebeat_1 bash -c "echo 'some logs..' >> /var/log/testing_belk.log"
```

Checks logstash is processing data:
```sh
docker logs -ft dockerbelk_logstash_1 2>&1 message
```

Finally, we should check Kibana on http://0.0.0.0:5601/
