# --
# File: phgenerator_consts.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2016
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

GEN_TEST_CONN_SUCCESS = "Test connectivity to nowhere has passed."
GEN_TEST_CONN_FAIL = "Test connectivity to nowhere has passed."
GEN_MAX_CONTAINERS = 10
GEN_MAX_ARTIFACTS = 10
#
# goes to /opt/phantom/apps/data/<app_id>/
USER_INC_FILEPATH = '../data/generator_'
FILE_ARTIFACT_DUMP = 'inc/artifact_dump.txt'
FILE_CEF_SAMPLE = 'inc/cef_sample.json'
FILE_FIELD_TYPES = 'inc/field_types.json'
FILE_CONTAINER_DEF = 'inc/container_definitions.json'
FILE_ARTIFACT_DEF = 'inc/artifact_definitions.json'
FILE_INCIDENT_NAMES = 'inc/event_names.txt'
#
GEN_CONTAINER_PREFIX = "Sample event"
GEN_ARTIFACT_PREFIX = "Sample artifact"
GEN_ARTIFACT_LABEL = "event"
#
GEN_CONTAINER_TAG = ""
GEN_ARTIFACT_TAG = ""
# maximum number of containers and artifacts to ever create
GEN_ABSOLUTE_MAX_CONTAINERS = 1000
GEN_ABSOLUTE_MIN_CONTAINERS = 1
GEN_ABSOLUTE_MAX_ARTIFACTS = 1000
GEN_ABSOLUTE_MIN_ARTIFACTS = 1
#
# generate cef artifacts with between 2 and 8 randomized keys.
GEN_CEF_MIN_FIELDSAMPLES = 2
GEN_CEF_MAX_FIELDSAMPLES = 8
#
DUE_SLA_DELTA_MIN = 30
DUE_SLA_DELTA_MAX = 60
DUE_SLA_DELTA_UNITS = "minutes"
#