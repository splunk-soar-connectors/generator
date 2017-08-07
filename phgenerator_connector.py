# --
# File: phgenerator_connector.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2017
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

# Phantom imports
import os
import time
from datetime import timedelta
import phantom.app as phantom
from phantom.app import BaseConnector

from PhantomFieldGenerator import *
from phgenerator_consts import *


class GeneratorConnector(BaseConnector):

    # code that decides what to name artifacts based on their cef content keys
    def _get_artifact_name(self, artifact_item):
        # self.artifactnames_filein
        try:
            # self.debug_print("ART FILE: {} - {}".format(self.artifactnames_filein, type(self.artifactnames_filein)))
            for artitem in self.artifactnames_filein:
                # .debug_print('ARTITEM: {} - {} - {}'.format(artitem, type(artitem), len(artitem)))
                # self.debug_print('ARTITEM2: {} - {}'.format(artifact_item['cef'], type(artifact_item['cef'])))
                for key, value in artitem.iteritems():
                    # self.debug_print('LOOP - {} - {}'.format(key, value))
                    for artkey, artvalue in (artifact_item.get('cef', {})).iteritems():
                        if artvalue.strip() == "":
                            continue
                        # self.debug_print('LOOP2 - {} - {}'.format(key, artkey))
                        if key.lower() in artkey.lower():
                            # self.debug_print('LOOPMATCH')
                            # self.debug_print("ART VALUE: {}".format(value))
                            return value
        except Exception as e:
            self.save_progress("get_artifact_name Artifact Exception: {}".format(e))
        return 'Unknown Artifact'  # default name if none found

    # code that pulls event names from a data file and returns a list of values
    def _get_random_names(self, file_in):
        names = []
        with open(str(file_in), 'r') as file:
            for lineno, line in enumerate(file):
                if self.is_poll_now():
                    self.send_progress("Reading line in event name data file: {}".format(lineno + 1))
                names.append(line)
        return names

    def _load_file_dicts(self, complete_filepath):
        dicts_from_file_list = list()
        with open(complete_filepath, 'r') as inf:
            for lineno, line in enumerate(inf):
                if self.is_poll_now():
                    self.send_progress("Reading line in event data file: {}".format(lineno + 1))
                dicts_from_file_list.append(eval(line))

        # dicts_from_file now contains the dictionaries created from the text file
        return dicts_from_file_list

    def _getfile(self, filename):
        with open(filename, 'r') as myfile:
            data = myfile.read()
        return data

    def _load_file_json(self, complete_filepath):
        with open(complete_filepath) as data_file:
            return_dict = json.load(data_file)
        return return_dict

    def _on_poll(self, param):

        # self.debug_print("entering onpoll action")
        # Get the maximum number of emails that we can pull
        config = self.get_config()

        # self.debug_print(config)

        # import pdb;pdb.set_trace()
        # default the max emails to the normal on_poll max emails
        if self.is_poll_now():
            domax_containers = param.get('container_count')
            domax_artifacts = param.get('artifact_count')
            # self.debug_print("maxc: {} - maxa: {}".format(domax_containers, domax_artifacts))
        else:
            domax_containers = int(config.get('create_containers', GEN_MAX_CONTAINERS))
            domax_artifacts = int(config.get('create_artifacts', GEN_MAX_ARTIFACTS))
        # catch for min/max values - never less than 1, never more than const max.
        domax_containers = min(domax_containers, GEN_ABSOLUTE_MAX_CONTAINERS)
        domax_artifacts = min(domax_artifacts, GEN_ABSOLUTE_MAX_ARTIFACTS)
        domax_containers = max(domax_containers, GEN_ABSOLUTE_MIN_CONTAINERS)
        domax_artifacts = max(domax_artifacts, GEN_ABSOLUTE_MIN_ARTIFACTS)
        #
        if self.is_poll_now():
            self.save_progress(
                "Generating {} events with up to {} randomized artifacts each".format(domax_containers, domax_artifacts))
        artifact_label = config.get('artifact_label', GEN_ARTIFACT_LABEL)
        artifact_prefix = config.get('artifact_prefix', GEN_ARTIFACT_PREFIX)
        container_prefix = config.get('container_prefix', GEN_CONTAINER_PREFIX)
        container_tag = config.get('container_tag', GEN_CONTAINER_TAG)
        artifact_tag = config.get('artifact_tag', GEN_ARTIFACT_TAG)
        data_filepath = config.get('source_data_file', FILE_ARTIFACT_DUMP)
        incident_name_filepath = config.get('source_name_file', FILE_INCIDENT_NAMES)
        #
        # min and max # of cef fields we try to randomize into an artifact
        mingen_ceffields = config.get('min_cef_per_artifact', GEN_CEF_MIN_FIELDSAMPLES)
        maxgen_ceffields = config.get('max_cef_per_artifact', GEN_CEF_MAX_FIELDSAMPLES)
        #
        # SLA DELTAS - set to a static range for now, later versions could implement the option.
        due_sla_deltamin = DUE_SLA_DELTA_MIN
        due_sla_deltamax = DUE_SLA_DELTA_MAX
        due_sla_deltaunits = DUE_SLA_DELTA_UNITS
        #
        #
        # find the app filepath
        useinc_filepath = os.path.dirname(__file__) + '/'
        # self.debug_print("inc_filepath: {}".format(useinc_filepath))
        #
        # make include data path if it doesnt exist
        user_data_filepath = os.path.join(useinc_filepath, USER_INC_FILEPATH + self.get_app_id())
        if not os.path.exists(user_data_filepath):
            os.makedirs(user_data_filepath, 0775)
        # self.debug_print("user filepath: {} ".format(user_data_filepath))
        # self.debug_print("maxc: {} - maxa: {}".format(domax_containers, domax_artifacts))
        #
        #
        # set data file to builtin by const file or by user string to apps/data/generator dir
        if data_filepath == FILE_ARTIFACT_DUMP:
            artifact_datafile = useinc_filepath + FILE_ARTIFACT_DUMP
        else:
            artifact_datafile = os.path.normpath(user_data_filepath + '/' + data_filepath)
        #
        # set name file to builtin by const file or by user string to apps/data/generator dir
        if incident_name_filepath == FILE_INCIDENT_NAMES:
            incident_datafile = useinc_filepath + FILE_INCIDENT_NAMES
        else:
            incident_datafile = os.path.normpath(user_data_filepath + '/' + incident_name_filepath)
        # self.debug_print("artifact_datafile: {}".format(artifact_datafile))
        #
        #
        try:
            fieldtype_filein = self._getfile(useinc_filepath + FILE_FIELD_TYPES)
            containerdef_filein = self._getfile(useinc_filepath + FILE_CONTAINER_DEF)
            artifactdef_filein = self._getfile(useinc_filepath + FILE_ARTIFACT_DEF)
            cef_sample_json = self._load_file_json(useinc_filepath + FILE_CEF_SAMPLE)
            sample_dictlist = self._load_file_dicts(artifact_datafile)
            self.artifactnames_filein = self._load_file_json(useinc_filepath + FILE_ARTIFACT_NAMES)
        except Exception as e:
            # self.save_progress("exception in file load: {}".format(e))
            # self.debug_print("exception in file load: {}".format(e))
            return self.set_status(phantom.APP_ERROR,
                                   "Exception Loading Event Data File: {}\nYou may want to check the line number listed above for errors.\n --- Error: {}".format(
                                       artifact_datafile, e))

        # self.debug_print("entering onpoll action - after files read ")
        pfg = PhantomFieldGenerator()

        # self.debug_print(" 2 entering onpoll action - after files read ")
        pfg.load_fieldtypes(fieldtype_filein)
        pfg.load_restmodel('container', containerdef_filein)
        pfg.load_restmodel('artifact', artifactdef_filein)

        # self.debug_print(" 3 entering onpoll action - after files read ")
        # Create arguments that add the cef data on generate
        cef_json_create = {'cef_sample_dict': cef_sample_json, 'value_override_dictlist': sample_dictlist,
                           'min_ceffields': mingen_ceffields, 'max_ceffields': maxgen_ceffields}
        pfg.create_dataargs('add', 'artifact', 'cef', cef_json_create)
        # self.debug_print("min/max: {}".format(cef_json_create))
        # end data generate CEF model addition

        # SLA Deltas - for now lets just create a static due delta and not set close/end time.
        # |    | &{close_time_args} | Create Dictionary | delta_min=4 | delta_max=20 | delta_unit=minutes |
        # |    | &{due_time_args} | Create Dictionary | delta_min=10 | delta_max=30 | delta_unit=minutes |
        # |    | &{end_time_args} | Create Dictionary | delta_min=5 | delta_max=15 | delta_unit=minutes |
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | close_time | ${close_time_args}
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | due_time | ${due_time_args}
        # |    | PhantomFieldGenerator.Create Dataargs | add | container | end_time | ${end_time_args}
        due_time_args = {'delta_min': due_sla_deltamin, 'delta_max': due_sla_deltamax, 'delta_unit': due_sla_deltaunits}
        pfg.create_dataargs('add', 'container', 'due_time', due_time_args)
        # end SLA section
        #
        # self.debug_print(" 4 entering onpoll action - after files read ")
        assetid = self.get_asset_id()
        pfg.field_override('modify', 'container', 'asset_id', assetid)
        pfg.field_override('modify', 'container', 'status', 'new')
        pfg.field_override('delete', 'container', 'close_time')
        pfg.field_override('delete', 'container', 'owner_id')
        pfg.field_override('modify', 'artifact', 'label', artifact_label)
        pfg.field_override('modify', 'container', 'name', container_prefix)
        pfg.field_override('modify', 'artifact', 'name', artifact_prefix)
        pfg.field_override('modify', 'artifact', 'type', 'event')
        pfg.field_override('modify', 'container', 'description', container_prefix)
        pfg.field_override('modify', 'artifact', 'run_automation', False)
        # allow tags to be added (maybe just one, unsure ;)
        if container_tag != "":
            pfg.field_override('modify', 'container', 'tags', container_tag)
        if artifact_tag != "":
            pfg.field_override('modify', 'artifact', 'tags', artifact_tag)
        # self.debug_print(" 5 entering onpoll action - after files read ")
        # self.debug_print("maxc: {} - maxa: {}".format(domax_containers, domax_artifacts))
        if self.is_poll_now():
            self.send_progress("Generating {} events".format(domax_containers))
        generated_data = pfg.create_many('sequential', domax_containers, container='random')
        # self.debug_print(" 6 entering onpoll action - after files read ")
        # generated_data = pfg.create_many('sequential', domax_artifacts, artifact='random')

        # self.debug_print(" 7 entering onpoll action - after files read ")
        # generated_data = pfg.modify_model('artifact', 'sequential', 'ipaddr', 'cef', 'destinationAddress', '2.2.4.0' )
        # generated_data = pfg.modify_model('artifact', 'sequential', 'ipaddr', 'cef', 'sourceAddress', '7.3.4.0' )

        # delete dst field out of cef entries
        # generated_data = pfg.modify_model('artifact', 'delete', 'null', 'cef', 'dst', 'null')

        # self.debug_print("entering creation")
        container_count = 0
        # artifact_count = 0
        #
        # get list of event names to be randomly picked while adding to containers that are posted
        event_names = self._get_random_names(incident_datafile)
        #
        for container_item in generated_data['container']:
            container_item['name'] = container_item['name'] + " " + str(random.choice(event_names))
            # prev cid location
            if self.is_poll_now():
                self.send_progress("Generating artifacts for event.")
            # generate new artifacts for this container
            generated_data = pfg.create_many('sequential', domax_artifacts, artifact='random')
            added_event_name = False
            # self.debug_print('DEBUG2: Generated type: {}'.format(type(generated_data)))
            ready_artifacts = []
            for artifact_count, artifact_item in enumerate(generated_data['artifact']):
                found_event_name = artifact_item.get('cef', {}).get('phantom_eventName', None)
                if found_event_name and found_event_name != "":
                    if not added_event_name:
                        # self.debug_print('DEBUG2: Found eventName: {}'.format(found_event_name))
                        container_item['name'] = found_event_name.strip()
                        added_event_name = True
                        artifact_item['name'] = (artifact_prefix + " " + self._get_artifact_name(artifact_item)).strip()
                        ready_artifacts.append(artifact_item)
                        del ready_artifacts[-1]['cef']['phantom_eventName']  # remove the event name so it doesnt get added as cef data.
                    else:  # if its an event name, and we've already found one, we don't want to add this one.
                        pass
                else:  # if its not an event name, we can add it.
                    artifact_item['name'] = (artifact_prefix + " " + self._get_artifact_name(artifact_item)).strip()
                    ready_artifacts.append(artifact_item)
            if len(ready_artifacts) > 0:  # make the very last artifact we've added run automation.
                    ready_artifacts[-1]['run_automation'] = True
            # start posting, save the container, then run through artifacts filtered above.
            container_item['artifacts'] = ready_artifacts

            with open('/tmp/container.txt', 'w') as outfile:
                json.dump(container_item, outfile)

            cstatus, cmsg, cid = self.save_container(container_item)
            container_count += 1
            if self.is_poll_now():
                self.send_progress("Added to container: {}".format(cid))
            generated_data.pop("artifact", None)  # remove the used artifacts

        return self.set_status(phantom.APP_SUCCESS)

    def _test_connectivity(self, param):

        self.save_progress(GEN_TEST_CONN_SUCCESS)

        return self.set_status(phantom.APP_SUCCESS, GEN_TEST_CONN_SUCCESS)

    def handle_action(self, param):
        """Function that handles all the actions

        Args:

        Return:
            A status code
        """

        result = None
        action = self.get_action_identifier()

        # self.debug_print("entering handle action")
        #


        if (action == phantom.ACTION_ID_INGEST_ON_POLL or action == 'on_poll'):
            start_time = time.time()
            result = self._on_poll(param)
            end_time = time.time()
            diff_time = end_time - start_time
            human_time = str(timedelta(seconds=int(diff_time)))
            self.save_progress("Time taken: {0}".format(human_time))
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            result = self._test_connectivity(param)

        return result

if __name__ == '__main__':
    import sys
    import json
    in_json = None
    in_email = None
    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        connector = GeneratorConnector()
        connector.print_progress_message = True
        if (len(sys.argv) == 2):
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

        print result

    exit(0)
