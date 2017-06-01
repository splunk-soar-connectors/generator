# --
# File: PhantomFieldGenerator.py
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
import datetime
from collections import defaultdict
import random, string
import json
from copy import deepcopy
# import time
__version__ = '0.1c'

# debug_level = "debug"
# debug_level = "none"

# allows a variety of debug levels to be displayed
# info will display error and info level
# def LogOutput(Level, **kwargs):
#    if (debug_level == "debug" and Level == "debug"):
#        for key, value in kwargs.iteritems():
#            #print "%s == %s" %(key,value)
#            #logger.debug('{} == {}'.format(key, value))
#    elif ((debug_level == "debug" or debug_level == "info") and (Level == "info")):
#        for key, value in kwargs.iteritems():
#            #print "%s == %s" %(key,value)
#            #logger.info('{} == {}'.format(key, value))
#    elif (Level == "error"):
#        for key, value in kwargs.iteritems():
#            #print "%s == %s" %(key,value)
#            #logger.error('{} == {}'.format(key, value))


def load_file_json(complete_filepath):
    try:
        with open(complete_filepath) as data_file:
            return_dict = json.load(data_file)
            # LogOutput('debug', message='success loading file {}'.format(complete_filepath))
            return return_dict
    except:
        # LogOutput('error', message='error loading file {}, {}'.format(complete_filepath, sys.exc_info()))
        return False

def write_file_json(complete_filepath, output_dict):
    try:
        with open(complete_filepath, 'w') as data_file:
            json.dump(output_dict, data_file)
            # LogOutput('debug', message='success writing file {}'.format(complete_filepath))
            return True
    except:
        # LogOutput('error', message='error writing file {}, {}'.format(complete_filepath, sys.exc_info()))
        return False

class PhantomFieldGenerator(object):
    def __init__(self):
        self.restmodel = {}  # this is where the sample model is loaded (definitions) to create output data
        self.restmodel_fieldoverride = defaultdict(list)  # this can be set using field_override to set manual values in fields when randomly creating other data
        self.generated_model = defaultdict(list)  # when using create_many this is where the large data model is stored
        # self.create_data_args -- was going to use to load cef file, then decided to use field override instead
        self.create_data_args = defaultdict(lambda: defaultdict())  # this can be set to provide arguments to the random field generator routine for a particular label

    def load_fieldtypes(self, fieldtype_json):
        self.fieldtypes = json.loads(fieldtype_json)
        # return self.fieldtypes

# load_restmodel loads a rest model into a dictionary using label as key
# so we can store multiple rest models
    def load_restmodel(self, label, restmodel_json):  # label would be, for example, container, or asset
        self.restmodel[label] = json.loads(restmodel_json)
        # return self.restmodel

# delete_restmodel allows deletion of a particular rest model from the dictionary
    def delete_restmodel(self, label):  # label would be, for example, container, or asset
        del self.restmodel[label]
        del self.restmodel_fieldoverride[label]
        # return self.restmodel

# allows override of a particular rest field, to prevent it from being overwritten by random values
# action can be modify or delete; delete allows the field to be removed completely from the dict data/eventual json data
# modify can be used to either modify an existing field or add a new one
    def field_override(self, action, label, field, fieldvalue=None):  # label would be, for example, container, or asset
        if action == 'modify':
            self.restmodel_fieldoverride[label].append(field)
            self.restmodel[label][field] = fieldvalue
        elif action == 'delete':
            self.restmodel_fieldoverride[label].append(field)
            del self.restmodel[label][field]

# allows removel of override of a particular rest field, to prevent it from being overwritten by random values
    def remove_field_override(self, label, field):  # label would be, for example, container, or asset
        try:
            self.restmodel_fieldoverride[label].remove(field)
            return True
        except:
            return False

# allows creation of arguments that are used later in generating the fields randomly
# helps control things like timestamp values, but still allow randomness
    def create_dataargs(self, action, label, field, fieldvalue=None):  # label would be, for example, container, or asset
        # LogOutput('debug', create_dataargs='action: {} label: {} field: {} fieldval: {}'.format(action, label, field, fieldvalue))
        if action == 'add':
            self.create_data_args[label][field] = fieldvalue
        elif action == 'delete':
            del self.create_data_args[label][field]

    def generate_rnd_int(self):
        return random.randint(0, 999999)

# FIXME: This actually needs to generate a list of random users based on the system
# list of users, user 1 is admin so that should work for the moment
    def generate_sys_rnd_user_int_list(self):
        return list(1)


# # generate_rnd_timestamp_iso8601tz examples for altering time, should also be able to use negative values
#===============================================================================
# |    | &{close_time_args} | Create Dictionary | delta_min=24 | delta_max=48 | delta_unit=hours |
# |    | &{due_time_args} | Create Dictionary | delta_min=36 | delta_max=64 | delta_unit=hours |
# |    | &{end_time_args} | Create Dictionary | delta_min=5 | delta_max=15 | delta_unit=minutes |
# |    | PhantomFieldGenerator.Create Dataargs | add | container | close_time | ${close_time_args}
# |    | PhantomFieldGenerator.Create Dataargs | add | container | due_time | ${due_time_args}
# |    | PhantomFieldGenerator.Create Dataargs | add | container | end_time | ${end_time_args}
#===============================================================================
    def generate_rnd_timestamp_iso8601tz(self, delta_min=0, delta_max=0, delta_unit='hours'):
        # LogOutput('debug', generate_8601tz='dmin: {} dmax: {} dunit: {}'.format(delta_min, delta_max, delta_unit))
        if delta_min == 0 and delta_max == 0:
            d = datetime.datetime.utcnow()
        else:
            timeset = random.randint(int(delta_min), int(delta_max))
            if delta_unit == 'hours':
                d = datetime.datetime.utcnow() + datetime.timedelta(hours=timeset)
            elif delta_unit == 'minutes':
                d = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeset)
            elif delta_unit == 'seconds':
                d = datetime.datetime.utcnow() + datetime.timedelta(seconds=timeset)
            elif delta_unit == 'microseconds':
                d = datetime.datetime.utcnow() + datetime.timedelta(microseconds=timeset)
            else:
                d = datetime.datetime.utcnow() + datetime.timedelta(days=timeset)
        # LogOutput('debug', generate_8601tz_d='d:{}'.format(d))
        return d.isoformat("T") + "Z"

    def generate_rnd_timestamp_iso8601(self):
        d = datetime.datetime.utcnow()
        return d.isoformat("T") + "+00:00"

    def generate_rnd_json_custom(self, size=13):
        char_set = string.ascii_letters + string.digits
        sample_dict = {}
        sample_dict[(''.join(random.sample(char_set * size, size)))] = (''.join(random.sample(char_set * size, size)))
        return sample_dict

    def generate_rnd_json_custom_fixedname(self, size=13):
        char_set = string.ascii_letters + string.digits
        sample_dict = {}
        sample_dict['data_field1'] = (''.join(random.sample(char_set * size, size)))
        return sample_dict

    def generate_sample_json_cef(self, cef_sample_fullfilepath):
        sample_dict = load_file_json(cef_sample_fullfilepath)
        return sample_dict

    def generate_rnd_json_cef(self, size=13):
        char_set = string.ascii_letters + string.digits
        sample_dict = {}
        sample_dict[(''.join(random.sample(char_set * size, size)))] = (''.join(random.sample(char_set * size, size)))
        return sample_dict

# FIXME: Finish this ---- to handle > 255 IPs
    def generate_sequential_ip_addr(self, quantity, seed_ipaddr='10.102.10.192'):
        ip_list = seed_ipaddr.split('.')
        newip_list = []
        if int(quantity) <= 255:
            for x in range(0, int(quantity)):
                ip_list[3] = x
                newip_list.append((str(ip_list[0]) + '.' + str(ip_list[1]) + '.' + str(ip_list[2]) + '.' + str(ip_list[3])))
        else:
            pass
            # LogOutput('error', generatesequential_ipaddr='Unhandled exception, can only generate up to 255 for now')
        return newip_list

# loads the sample json dict and then uses dict_override to override the fields
# value_override_list will be a list of dicts, each dict from one line of the file
# See PhantomAutomationTools.Load File Dicts
#===============================================================================
# |    | &{cef_json_create} | Create Dictionary | cef_sample_dict=${cef_sample_json} | value_override_dictlist=${isight_sample_dictlist} |
# |    | PhantomFieldGenerator.Create Dataargs | add | artifact | cef | ${cef_json_create}
#===============================================================================
    def generate_rnd_sample_json_cef(self, cef_sample_dict="", value_override_dictlist="", min_ceffields="", max_ceffields=""):
        if (cef_sample_dict == "" or value_override_dictlist == ""):
            pass
            # LogOutput('debug', gen_rnd_sample_json_cef='You failed to provide create dataargs for this field to work')
        else:
            sample_dict = deepcopy(cef_sample_dict)
            for _ in range(random.randint(int(min_ceffields), int(max_ceffields))): # pick between 2 and 8 keys to add and override
                pickakey = random.randint(0, (len(value_override_dictlist) - 1))
                # LogOutput('debug', gen_rnd_sample_json_cef2='pkey: {} - vodl: {}'.format(pickakey, value_override_dictlist[pickakey]))
                for key, value in value_override_dictlist[pickakey].iteritems():  # pick one of the items in the list, it's a dict, so then use the key/values inside to overwrite
                    sample_dict[key] = value
            return sample_dict

    def generate_rnd_string(self):
        char_set = string.ascii_letters + string.digits
        return ''.join(random.sample(char_set * 26, 26))

    def generate_rnd_string_lower(self):
        char_set = string.ascii_lowercase + string.digits
        return ''.join(random.sample(char_set * 26, 26))

    def generate_rnd_string_userid(self):
        char_set = string.ascii_letters + string.digits
        return ''.join(random.sample(char_set * 13, 13)) + "@" + ''.join(random.sample(char_set * 13, 13)) + "." + ''.join(random.sample(char_set * 3, 3))

    def generate_rnd_string_sensitivity(self):
        rndchoice = random.randint(0, (len(self.fieldtypes['fieldtypes']['string_sensitivity']['values']) - 1))
        # #LogOutput('info', message=self.fieldtypes['fieldtypes']['sensitivity']['values'])
        return self.fieldtypes['fieldtypes']['string_sensitivity']['values'][rndchoice]

    def generate_rnd_string_severity(self):
        rndchoice = random.randint(0, (len(self.fieldtypes['fieldtypes']['string_severity']['values']) - 1))
        # #LogOutput('info', message=self.fieldtypes['fieldtypes']['string_severity']['values'])
        return self.fieldtypes['fieldtypes']['string_severity']['values'][rndchoice]

    def generate_rnd_status(self):
        rndchoice = random.randint(0, (len(self.fieldtypes['fieldtypes']['string_status']['values']) - 1))
        # #LogOutput('info', message=self.fieldtypes['fieldtypes']['status']['values'])
        return self.fieldtypes['fieldtypes']['string_status']['values'][rndchoice]

#===============================================================================
# #
# ## create phase- json, specify container api and random creation method
# #
# |    | PhantomFieldGenerator.Load Fieldtypes | ${fieldtype_filein}
# |    | PhantomFieldGenerator.Load Restmodel | container | ${container_filein}
# |    | PhantomFieldGenerator.Load Restmodel | artifact | ${artifact_filein}
# |    | &{cef_json_create} | Create Dictionary | cef_sample_dict=${cef_sample_json} | value_override_dictlist=${isight_sample_dictlist} |
# |    | PhantomFieldGenerator.Create Dataargs | add | artifact | cef | ${cef_json_create}
# |    | PhantomFieldGenerator.Field Override | modify | container | asset_id | ${fixed_asset_id} |
# |    | PhantomFieldGenerator.Field Override | delete | container | owner_id |
# #|    | PhantomFieldGenerator.Field Override | modify | artifact | cef | ${cef_sample_json} |
# # this type of create will create x containers with y artifacts each
# |    | ${generated_data}= | PhantomFieldGenerator.Create Many | sequential | ${quantity_create_containers} | container=random |
# |    | ${generated_data}= | PhantomFieldGenerator.Create Many | sequential | ${quantity_create_artifacts} | artifact=random |
# # this create example shows how you can have it create x containers with x artifacts each
# # |    | ${generated_data}= | PhantomFieldGenerator.Create Many | sequential | ${quantity_create_items} | container=random | artifact=random |
# #|    | Log | \nGenerated data: ${generated_data} | console=yes
#===============================================================================
# create_many and run_many --
# this can be used to create many data transactions
# method provides some logic to how to create the items
# 'sequential' -- basically create one of each item at a time
    def create_many(self, method, quantity, **kwargs):
        x = 0
        if method == 'sequential':
            while x <= (int(quantity) - 1):
                for label, method in kwargs.iteritems():
                    self.generated_model[label].append(self.create_data(label, method))
                x += 1
        return self.generated_model

# Calling this will wipe the existing generated model, used in tests where we want to wipe the data and re-generate new data.
    def wipe_model(self):
        self.generated_model = defaultdict(list)
        return self.generated_model
#
# allows modification of existing generated model, ie for changing cef fields
# method describes the method to use (sequential or random creation, or delete)
# datatype describes the type of  data to change, ie, ip address
# field is which cef field to modify
# label is what to modify, ie container/artifact
# locale is cef for now
# seed is seed data for the process
# FIXME: for now this will modify all the fields in the entire generated model for the particular label
# modify cef fields to have sequentially different IP addresses
#===============================================================================
# |    | ${generated_data}= | PhantomFieldGenerator.Modify Model | artifact | sequential | ipaddr | cef | destinationAddress | 2.2.4.0 |
# |    | ${generated_data}= | PhantomFieldGenerator.Modify Model | artifact | sequential | ipaddr | cef | sourceAddress | 7.3.4.0 |
# # delete dst field out of cef entries
# |    | ${generated_data}= | PhantomFieldGenerator.Modify Model | artifact | delete | null | cef | dst | null |
#===============================================================================
    def modify_model(self, label, method, datatype, locale, field, seed):
        if label == 'artifact':
            if method == 'sequential':
                if locale == 'cef':
                    if datatype == 'ipaddr':
                        quantity = len(self.generated_model[label])
                        newip_list = self.generate_sequential_ip_addr(quantity, seed)  # seed should be ip address
                        for x in range(0, len(self.generated_model[label])):
                            self.generated_model[label][x]['cef'][field] = newip_list[x]
            if method == "delete":
                if locale == 'cef':
                    for x in range(0, len(self.generated_model[label])):
                        del self.generated_model[label][x]['cef'][field]
        return self.generated_model

# FIXME: this is only geared towards creating the first level json data (ie, first level dictionary) at this time
# will have to figure out how to deal with multi-level json data in the future
# FIXMEFIXED?: The submodules below can handle creating the second layer of json, for examples see json_rnd_sample_cef
    def create_data(self, label, method):
        # LogOutput('debug', create_data1='Creating \'{}\' json data, using method: \'{}\''.format(label, method))
        gendict = {}
        for key, value in self.restmodel[label].iteritems():
            if not key in self.restmodel_fieldoverride[label]:  # manual override random generation of this particular field
                # LogOutput('debug', create_data2='Key {} - Value {}'.format(key,value))
                if method == 'random':
                    options = {'int' : self.generate_rnd_int,
                               'sys_user_int_list' : self.generate_sys_rnd_user_int_list,
                               'timestamp_iso8601' : self.generate_rnd_timestamp_iso8601tz,
                               'json_custom' : self.generate_rnd_json_custom,
                               'json_custom_fixedname' : self.generate_rnd_json_custom_fixedname,
                               'json_cef' : self.generate_sample_json_cef,
                               'json_rnd_sample_cef' : self.generate_rnd_sample_json_cef,
                               'string' : self.generate_rnd_string,
                               'string_lower' : self.generate_rnd_string_lower,
                               'string_userid' : self.generate_rnd_string_userid,
                               'string_sensitivity' : self.generate_rnd_string_sensitivity,
                               'string_severity' : self.generate_rnd_string_severity,
                               'string_unique' : self.generate_rnd_string,
                               'string_status' : self.generate_rnd_status,
                    }
                    if label not in list(self.create_data_args.keys()):
                        gendict[key] = options[value]()
                    else:
                        if key not in list(self.create_data_args[label].keys()):
                            gendict[key] = options[value]()
                        else:
                            gendict[key] = options[value](**self.create_data_args[label][key])
            else:
                gendict[key] = self.restmodel[label][key]  # add whatever value already existed in this field
            # LogOutput('debug', gendict='gendict:{}'.format(gendict[key]))
        return gendict

if __name__ == '__main__':
    # LogOutput("info", message="Sample output from #logger")
    pass
