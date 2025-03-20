# File: phgenerator_connector.py
#
# Copyright (c) 2016-2025 Splunk Inc.
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
#
#
# Phantom imports
import os
import random
import time
from datetime import timedelta

import phantom.app as phantom
import requests
from phantom.app import BaseConnector

from PhantomFieldGenerator import *
from phgenerator_consts import *


class GeneratorConnector(BaseConnector):
    def __init__(self):
        # Call the BaseConnectors init first
        super().__init__()

        self._severity = None
        self._severities = None
        self._status = None
        self._statuses = None
        self._new_statuses = None

    def initialize(self):
        # Support custom severities and statuses
        config = self.get_config()
        action = self.get_action_identifier()
        test_connectivity = False

        verify_server_cert = config.get("verify_server_cert", False)

        if action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY or action == "test_connectivity":
            test_connectivity = True

        try:
            r = requests.get(f"{self._get_phantom_base_url()}rest/container_options", verify=verify_server_cert, timeout=DEFAULT_TIMEOUT)
            resp_json = r.json()
        except Exception as e:
            return self.set_status(phantom.APP_ERROR, f"Could not get severity and status options from platform: {e}")

        if r.status_code != 200:
            if test_connectivity:
                self.save_progress("Test Connectivity Failed")
            return self.set_status(
                phantom.APP_ERROR,
                "Could not get severity and status options from platform: {}".format(resp_json.get("message", "Unknown Error")),
            )

        self._severities = [s["name"] for s in resp_json["severity"]]
        self._severity = config.get("event_severity", "random").lower()

        if self._severity not in self._severities and self._severity != "random":
            if test_connectivity:
                self.save_progress("Test Connectivity Failed")
            return self.set_status(
                phantom.APP_ERROR,
                "Supplied severity, {}, not found in configured severities: {}".format(self._severity, ", ".join(self._severities)),
            )

        self._statuses = [s["name"] for s in resp_json["status"]]
        self._new_statuses = []
        for s in resp_json["status"]:
            if s["status_type"] == "new":
                self._new_statuses.append(s["name"])
        self._status = config.get("event_status", "random").lower()

        if self._status not in self._statuses and self._status != "random":
            if test_connectivity:
                self.save_progress("Test Connectivity Failed")
            return self.set_status(
                phantom.APP_ERROR, "Supplied status, {}, not found in configured statuses: {}".format(self._status, ", ".join(self._statuses))
            )

        return phantom.APP_SUCCESS

    # code that decides what to name artifacts based on their cef content keys
    def _get_artifact_name(self, artifact_item):
        # self.artifactnames_filein
        try:
            for artitem in self.artifactnames_filein:
                for key, value in list(artitem.items()):
                    for artkey, artvalue in list((artifact_item.get("cef", {})).items()):
                        if artvalue.strip() == "":
                            continue
                        if key.lower() in artkey.lower():
                            return value
        except Exception as e:
            self.save_progress(f"get_artifact_name Artifact Exception: {e}")
        return "Unknown Artifact"  # default name if none found

    # code that pulls event names from a data file and returns a list of values
    def _get_random_names(self, file_in):
        names = []
        with open(str(file_in)) as file:
            for lineno, line in enumerate(file):
                if self.is_poll_now():
                    self.send_progress(f"Reading line in event name data file: {lineno + 1}")
                names.append(line)
        return names

    def _load_file_dicts(self, complete_filepath):
        dicts_from_file_list = list()
        with open(complete_filepath) as inf:
            for lineno, line in enumerate(inf):
                if self.is_poll_now():
                    self.send_progress(f"Reading line in event data file: {lineno + 1}")
                dicts_from_file_list.append(eval(line))

        # dicts_from_file now contains the dictionaries created from the text file
        return dicts_from_file_list

    def _getfile(self, filename):
        with open(filename) as myfile:
            data = myfile.read()
        return data

    def _load_file_json(self, complete_filepath):
        with open(complete_filepath) as data_file:
            return_dict = json.load(data_file)
        return return_dict

    def _on_poll(self, param):
        # Get the maximum number of emails that we can pull
        config = self.get_config()

        # import pdb;pdb.set_trace()
        # default the max emails to the normal on_poll max emails
        if self.is_poll_now():
            domax_containers = param.get("container_count")
            domax_artifacts = param.get("artifact_count")
        else:
            domax_containers = int(config.get("create_containers", GEN_MAX_CONTAINERS))
            domax_artifacts = int(config.get("create_artifacts", GEN_MAX_ARTIFACTS))
        # catch for min/max values - never less than 1, never more than const max.
        domax_containers = min(domax_containers, GEN_ABSOLUTE_MAX_CONTAINERS)
        domax_artifacts = min(domax_artifacts, GEN_ABSOLUTE_MAX_ARTIFACTS)
        domax_containers = max(domax_containers, GEN_ABSOLUTE_MIN_CONTAINERS)
        domax_artifacts = max(domax_artifacts, GEN_ABSOLUTE_MIN_ARTIFACTS)

        # event owner range assigns a random event owner
        event_owner_range = config.get("event_owner_range", "0-0")
        randomize_event_owners = False
        try:
            start_owner_id = int(event_owner_range.strip().split("-")[0])
            end_owner_id = int(event_owner_range.strip().split("-")[1])
            randomize_event_owners = True
        except:
            start_owner_id = 0
            end_owner_id = 0
        if start_owner_id == 0 or end_owner_id == 0:
            randomize_event_owners = False
        if end_owner_id < start_owner_id:
            randomize_event_owners = False

        if self.is_poll_now():
            if config.get("artifact_count_override", False):
                self.save_progress(f"Forcing creation of {domax_artifacts} artifacts per event.")
            else:
                self.save_progress(f"NOT forcing artifact count. Generating UP TO {domax_artifacts} artifacts per event.")
            self.save_progress(f"Randomizing owners: {randomize_event_owners}")
            self.save_progress(f"Generating {domax_containers} events.")

        # find the app filepath
        useinc_filepath = os.path.dirname(__file__) + "/"
        if hasattr(self, "get_phantom_home"):
            phantom_home_path = self.get_phantom_home()
        else:
            phantom_home_path = "/opt/phantom"

        # make include data path if it doesnt exist
        user_data_filepath = os.path.join(useinc_filepath, phantom_home_path, USER_INC_FILEPATH + self.get_app_id())
        if not os.path.exists(user_data_filepath):
            os.makedirs(user_data_filepath, 0o775)

        # set data file to builtin by const file or by user string to apps/data/generator dir
        if config.get("source_data_file", FILE_ARTIFACT_DUMP) == FILE_ARTIFACT_DUMP:
            artifact_datafile = useinc_filepath + FILE_ARTIFACT_DUMP
        elif "inc/empty.txt" in config.get("source_data_file", FILE_ARTIFACT_DUMP):
            artifact_datafile = useinc_filepath + FILE_ARTIFACT_EMPTY
        else:
            artifact_datafile = os.path.normpath(user_data_filepath + "/" + config.get("source_data_file", FILE_ARTIFACT_DUMP))

        # set name file to builtin by const file or by user string to apps/data/generator dir
        if config.get("source_name_file", FILE_INCIDENT_NAMES) == FILE_INCIDENT_NAMES:
            incident_datafile = useinc_filepath + FILE_INCIDENT_NAMES
        else:
            incident_datafile = os.path.normpath(user_data_filepath + "/" + config.get("source_name_file", FILE_INCIDENT_NAMES))

        return self._on_poll_generate_artifacts(
            config,
            useinc_filepath,
            incident_datafile,
            artifact_datafile,
            domax_containers,
            domax_artifacts,
            start_owner_id,
            end_owner_id,
            randomize_event_owners,
        )

    def _on_poll_generate_artifacts(
        self,
        config,
        useinc_filepath,
        incident_datafile,
        artifact_datafile,
        domax_containers,
        domax_artifacts,
        start_owner_id,
        end_owner_id,
        randomize_event_owners,
    ):
        try:
            fieldtype_filein = self._getfile(useinc_filepath + FILE_FIELD_TYPES)
            containerdef_filein = self._getfile(useinc_filepath + FILE_CONTAINER_DEF)
            artifactdef_filein = self._getfile(useinc_filepath + FILE_ARTIFACT_DEF)
            cef_sample_json = self._load_file_json(useinc_filepath + FILE_CEF_SAMPLE)
            sample_dictlist = self._load_file_dicts(artifact_datafile)
            self.artifactnames_filein = self._load_file_json(useinc_filepath + FILE_ARTIFACT_NAMES)
        except Exception as e:
            return self.set_status(phantom.APP_ERROR, EXCEPTION_LOAD_EVENT_DATA.format(artifact_datafile, e))

        pfg = PhantomFieldGenerator()

        pfg.load_fieldtypes(fieldtype_filein)
        pfg.load_restmodel("container", containerdef_filein)
        pfg.load_restmodel("artifact", artifactdef_filein)

        # Create arguments that add the cef data on generate
        cef_json_create = {
            "cef_sample_dict": cef_sample_json,
            "value_override_dictlist": sample_dictlist,
            "min_ceffields": config.get("min_cef_per_artifact", GEN_CEF_MIN_FIELDSAMPLES),
            "max_ceffields": config.get("max_cef_per_artifact", GEN_CEF_MAX_FIELDSAMPLES),
        }
        pfg.create_dataargs("add", "artifact", "cef", cef_json_create)
        # end data generate CEF model addition

        # SLA Deltas - for now lets just create a static due delta and not set close/end time.
        # |    | &{close_time_args} | Create Dictionary | delta_min=4 | delta_max=20 | delta_unit=minutes |
        # |    | &{due_time_args} | Create Dictionary | delta_min=10 | delta_max=30 | delta_unit=minutes |
        # |    | &{end_time_args} | Create Dictionary | delta_min=5 | delta_max=15 | delta_unit=minutes |
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | close_time | ${close_time_args}
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | due_time | ${due_time_args}
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | end_time | ${end_time_args}
        due_time_args = {"delta_min": DUE_SLA_DELTA_MIN, "delta_max": DUE_SLA_DELTA_MAX, "delta_unit": DUE_SLA_DELTA_UNITS}
        pfg.create_dataargs("add", "container", "due_time", due_time_args)
        # end SLA section
        #
        assetid = int(self.get_asset_id())
        pfg.field_override("modify", "container", "asset_id", assetid)
        pfg.field_override("delete", "container", "close_time")
        pfg.field_override("delete", "container", "owner_id")
        pfg.field_override("modify", "artifact", "label", config.get("artifact_label", GEN_ARTIFACT_LABEL))
        pfg.field_override("modify", "container", "name", config.get("container_prefix", GEN_CONTAINER_PREFIX))
        pfg.field_override("modify", "artifact", "name", config.get("artifact_prefix", GEN_ARTIFACT_PREFIX))
        pfg.field_override("modify", "artifact", "type", "event")
        pfg.field_override("modify", "container", "description", config.get("container_prefix", GEN_CONTAINER_PREFIX))

        if config.get("event_sensitivity", "Random") != "Random":
            pfg.field_override("modify", "container", "sensitivity", config.get("event_sensitivity", "Random").lower())

        # pfg.field_override('delete', 'artifact', 'run_automation', False) # PS-8501 don't put run automation flag in when using save_container.
        # allow tags to be added (maybe just one, unsure ;)
        if config.get("container_tag", GEN_CONTAINER_TAG) != "":
            pfg.field_override("modify", "container", "tags", config.get("container_tag", GEN_CONTAINER_TAG))
        if config.get("artifact_tag", GEN_ARTIFACT_TAG) != "":
            pfg.field_override("modify", "artifact", "tags", config.get("artifact_tag", GEN_ARTIFACT_TAG))
        generated_data = pfg.create_many("sequential", domax_containers, container="random")
        container_count = 0
        # artifact_count = 0
        #
        # get list of event names to be randomly picked while adding to containers that are posted
        event_names = self._get_random_names(incident_datafile)
        #
        for container_item in generated_data["container"]:
            container_item["name"] = container_item["name"] + " " + str(random.choice(event_names))
            # prev cid location
            # if self.is_poll_now():
            #     self.send_progress("Generating artifacts for event.")
            # generate new artifacts for this container

            if self._severity != "random":
                severity = self._severity
            else:
                severity = random.choice(self._severities)

            container_item["severity"] = severity

            if self._status != "random":
                status = self._status
            else:
                if config.get("limit_status_to_new", True):
                    status = random.choice(self._new_statuses)
                else:
                    status = random.choice(self._statuses)

            container_item["status"] = status

            generated_data = pfg.create_many("sequential", domax_artifacts, artifact="random")
            added_event_name = False
            ready_artifacts = []
            for artifact_count, artifact_item in enumerate(generated_data["artifact"]):
                found_event_name = artifact_item.get("cef", {}).get("phantom_eventName", None)
                if found_event_name and found_event_name != "":
                    if not added_event_name:
                        container_item["name"] = found_event_name.strip()
                        # if the container name found is empty after stripping then provide at least the prefix.
                        if container_item["name"] == "":
                            container_item["name"] = config.get("container_prefix", GEN_CONTAINER_PREFIX)
                        added_event_name = True
                        artifact_item["name"] = (
                            config.get("artifact_prefix", GEN_ARTIFACT_PREFIX) + " " + self._get_artifact_name(artifact_item)
                        ).strip()
                        ready_artifacts.append(artifact_item)
                        del ready_artifacts[-1]["cef"]["phantom_eventName"]  # remove the event name so it doesnt get added as cef data.
                    else:  # if its an event name, and we've already found one, we don't want to add this one.
                        if config.get("artifact_count_override", False):
                            ready_artifacts.append(artifact_item)
                            del ready_artifacts[-1]["cef"]["phantom_eventName"]  # remove the event name so it doesnt get added as cef data.
                        pass
                else:  # if its not an event name, we can add it.
                    artifact_item["name"] = (
                        config.get("artifact_prefix", GEN_ARTIFACT_PREFIX) + " " + self._get_artifact_name(artifact_item)
                    ).strip()
                    ready_artifacts.append(artifact_item)
                artifact_item["severity"] = severity
            # start posting, save the container, then run through artifacts filtered above.
            container_item["artifacts"] = ready_artifacts

            # random event owner
            if randomize_event_owners:
                container_item["owner_id"] = random.randint(start_owner_id, end_owner_id)

            # For debugging only
            # with open('/tmp/container.txt', 'w') as outfile:
            #    json.dump(container_item, outfile)
            cstatus, cmsg, cid = self.save_container(container_item)
            container_count += 1
            if self.is_poll_now():
                if cid is None:
                    self.save_progress(f"Failed to generate container. {cmsg}")
                else:
                    self.send_progress(f"Added to container: {cid}")
            generated_data.pop("artifact", None)  # remove the used artifacts

        return self.set_status(phantom.APP_SUCCESS)

    def _test_connectivity(self):
        # If we are here we have successfully passed connectivity through initialize method
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")
        self.save_progress("Test Connectivity Passed")

        self.set_status(phantom.APP_SUCCESS, GEN_TEST_CONN_SUCCESS)
        return self.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param):
        """Function that handles all the actions

        Args:

        Return:
            A status code
        """

        result = None
        action = self.get_action_identifier()
        if action == phantom.ACTION_ID_INGEST_ON_POLL or action == "on_poll":
            start_time = time.time()
            result = self._on_poll(param)
            end_time = time.time()
            diff_time = end_time - start_time
            human_time = str(timedelta(seconds=int(diff_time)))
            self.save_progress(f"Time taken: {human_time}")
        elif action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY or action == "test_connectivity":
            result = self._test_connectivity()

        return result


if __name__ == "__main__":
    import json
    import sys

    in_json = None
    in_email = None
    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        connector = GeneratorConnector()
        connector.print_progress_message = True
        if len(sys.argv) == 2:
            result = connector._handle_action(json.dumps(in_json), None)
        else:
            with open(sys.argv[2]) as ie:
                # connector.set_input_json(in_json)
                connector._load_input_json()
                # result = connector._handle_action(json.dumps(in_json), None)
                # connector.set_config({
                #         IMAP_JSON_EXTRACT_DOMAINS: True,
                #         IMAP_JSON_EXTRACT_ATTACHMENTS: True,
                #         IMAP_JSON_EXTRACT_URLS: True,
                #         IMAP_JSON_EXTRACT_IPS: True,
                #         IMAP_JSON_EXTRACT_DOMAINS: True,
                #         IMAP_JSON_EXTRACT_HASHES: True})
                # connector.set_asset_id("1")
                connector._load_app_json()
                connector._init_ingestion_dicts()

        print(result)

    sys.exit(0)
