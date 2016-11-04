# microcosm-logging

Opinionated logging configuration using [microcosm](https://github.com/globality-corp/microcosm) wiring.

[![Circle CI](https://circleci.com/gh/globality-corp/microcosm-logging/tree/develop.svg?style=svg)](https://circleci.com/gh/globality-corp/microcosm-logging/tree/develop)


## Usage

    from microcosm.api import create_object_graph

    graph = create_object_graph(name="foo")
    graph.use("logger")


## Convention

 - Logging should "just work" without large amounts of configuration
 - Outside of development and unittesting, log aggregation should be automatic (e.g. to [loggly](https://www.loggly.com/))
 - INFO level logging should be the default behavior; third-party libraries that mistakenly spew output at INFO
   should be turned down by default


## Configuration

To set the global logging level to something other than info, use:

    config.logging.level = "WARN"

To enable loggly, set its `token` and configure an `environment` name:

    config.logging.loggly.token = "LOGGLY_TOKEN"
    config.logging.loggly.environment = "ENVIRONMENT_NAME"

To disable loggly unconditionally:

    config.logging.loggly.enabled = False

To tune the logging levels of third-party components:

    config.logging.loggly.levels.override.warn = ["foo", "bar"]
