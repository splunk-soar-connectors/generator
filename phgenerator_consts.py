# File: phgenerator_consts.py
#
# Copyright (c) 2016-2022 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
GEN_TEST_CONN_SUCCESS = "Test connectivity to nowhere has passed."
GEN_TEST_CONN_FAIL = "Test connectivity to nowhere has passed."
EXCEPTION_LOAD_EVENT_DATA = "Exception Loading Event Data File: {0}\nYou may want to check the line number listed above for errors.\n --- Error: {1}"
GEN_MAX_CONTAINERS = 10
GEN_MAX_ARTIFACTS = 10
#
USER_INC_FILEPATH = 'apps/data/generator_'
FILE_ARTIFACT_DUMP = 'inc/artifact_dump.txt'
FILE_ARTIFACT_EMPTY = 'inc/empty.txt'
FILE_CEF_SAMPLE = 'inc/cef_sample.json'
FILE_FIELD_TYPES = 'inc/field_types.json'
FILE_CONTAINER_DEF = 'inc/container_definitions.json'
FILE_ARTIFACT_DEF = 'inc/artifact_definitions.json'
# Artifact names provides a search criteria to determine based on cef field keys what an artifact name should be.
FILE_ARTIFACT_NAMES = 'inc/artifact_naming.json'
# event names are currently the container names that are used randomly if the artifact_dump file does not specify any via phantom_eventName key
FILE_INCIDENT_NAMES = 'inc/event_names.txt'
#
GEN_CONTAINER_PREFIX = "Detected event"
GEN_ARTIFACT_PREFIX = ""
GEN_ARTIFACT_LABEL = "event"
#
GEN_CONTAINER_TAG = ""
GEN_ARTIFACT_TAG = ""
# maximum number of containers and artifacts to ever create
GEN_ABSOLUTE_MAX_CONTAINERS = 20000
GEN_ABSOLUTE_MIN_CONTAINERS = 1
GEN_ABSOLUTE_MAX_ARTIFACTS = 1000
GEN_ABSOLUTE_MIN_ARTIFACTS = 1
#
# generate cef artifacts with between 2 and 4 randomized keys.
# limited to 2-4 because it generates more varied data than just file events this way.
GEN_CEF_MIN_FIELDSAMPLES = 2
GEN_CEF_MAX_FIELDSAMPLES = 4
#
DUE_SLA_DELTA_MIN = 30
DUE_SLA_DELTA_MAX = 60
DUE_SLA_DELTA_UNITS = "minutes"
#
