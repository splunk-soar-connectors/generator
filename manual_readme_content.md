This app will generate sample, semi-random data to be ingested at regular polling intervals.
Multiple assets can be created with differing configurations to produce multiple streams of
generated data.

## Poll Now

Poll now can be used to immediately ingest the specified number of events, each of which will
contain the specified number of artifacts.

## Scheduled Polling

This allows artifacts and events to be generated at the specified polling intervals automatically.

## Basic Asset Settings

**Events to generate:** When polling is enabled, generate this many events per poll.

**Artifacts per event to generate:** When polling is enabled, attempt to generate up to this many
artifacts. By default, artifacts that don't belong to the particular event will not be added.

**Force exact artifact count:** Default is unchecked, only artifacts related to the event will be
added. If checked, Generator will create the exact number of artifacts specified. This increases the
likelihood that the artifacts will be unrelated to the event.

**Event severity:** Default is Random. If Random, all events will be given a random severity from
the configured severities. Otherwise events will all be given the specified severity.

**Event status:** Default is Random. If Random, all events will be given a random status from the
configured statuses. Otherwise events will all be given the specified status.

**Limit event statuses to new status types:** Default is checked. If checked, and **Event status**
is Random, events will be given random statuses of type **new** .

**Event owner ID range:** Default (0-0) creates events with no owners. Specify a range of User IDs
on your instance (ie 2-5) and Generator will create events with those owners if they exist. If the
owner IDs do not exist, the events will fail to be added.

## Included data files:

Included data files are shipped with the app; you can use these as samples to create your own:\
Default (contains event names): [artifact_dump.txt](inc/artifact_dump.txt)\
Generator version 1 file: [artifact_dump_v1.txt](inc/artifact_dump_v1.txt)\
Generator version 2 file (copy of the default above):
[artifact_dump_v2.txt](inc/artifact_dump_v2.txt)

## Generated artifact modification: Custom data source files

Create a file in **/opt/phantom/apps/data/generator_48f16006-fee0-44fa-89b0-0106c0618527/** with a
useful name, such as "newdata.txt". If the path doesn't exist, make sure to complete an initial
"Poll Now" with the app to initialize it.\
**If you want to revert to Generator App v1 creation behavior, copy artifact_dump_v1.txt to the
above path, set the file permissions, and create an asset that uses this filename for the artifact
data file.**\
Ensure that the file permissions are correct: chown -R phantom-worker.phantom
/opt/phantom/apps/data/generator_48f16006-fee0-44fa-89b0-0106c0618527/\
In your generator asset's "asset settings" configuration, set the field "Artifact Data File" to the
filename, ie "newdata.txt". The file should contain on each line a valid python dict literal
containing CEF sample data. Items are chosen from this file to fill the various CEF fields. If you
want to make sure specific CEF fields appear in an artifact together, simply create a python dict
literal on one line that contains all the CEF fields and their values. If you want to add more
random data without correlating it to other CEF fields just add a simple python dict literal with
one CEF field and its value.

**Correlated data example (all three CEF fields will randomly appear in an artifact, possibly with
additional generated CEF data):**

```
{"cs1": "30968", "cs1Label": "asn", "destinationAddress": "77.221.140.99"}
```

**Simple data example (the defined CEF field will randomly appear in an artifact, possibly with
other generated CEF data):**

```
{"destinationAddress": "253.207.67.115"}
```

**Creating static event names with no real artifact data to be used as a generic cronjob event:**

**Adding a key value of phantom_eventName will allow the setting of the event name (container)
within Phantom. This field is not added to the cef data:**

*This disables randomized event names (see below), since the data set includes event names.*

```
{"phantom_eventName": "Variant of Win32/GameHack.ARC","fileHash": "31b72e15b9a1bd9128ee1e780af4ede1", "fileName": "WebUsko.exe"}
```

**If phantom_eventName is found, the configured event name prefix will be ignored, and to avoid
invalidating data any other artifacts with a phantom_eventName field will not be added to the
event.**

## Generated artifact modification: Data lines per artifact

The Min/Max data lines per artifact parameter allows you more control over combinations of CEF
fields placed into an artifact. Generator will try to create artifacts using a random number
(between min and max) of lines in the selected source data file. As described above, each line can
contain one or more CEF fields.

## Creating static event (container) names without artifact data (useful for generic timed event triggering)

Set the artifact data file field in the asset to "inc/empty.txt" without the quotes. The event
prefix name (required) becomes the static name for all events generated.

## Modifying randomized event (container) names

*This applies only when using a Generator version 1 formatted data file.*

Create a file in **/opt/phantom/apps/data/generator_48f16006-fee0-44fa-89b0-0106c0618527/** with a
useful name, such as "event_names.txt". If the path doesn't exist, make sure to complete an initial
"Poll Now" with the app to initialize it.\
Ensure that the file permissions are correct: chown phantom-worker.phantom.\
In your generator asset's "asset settings" configuration, set the field "Event Name File" to the
filename, ie "event_names.txt". The file should contain a list of phrases or words that you would
like the app to randomly pull from in order to have more selectable event (container) names that are
specific to your needs.

Default data file: [event_names.txt](inc/event_names.txt)
