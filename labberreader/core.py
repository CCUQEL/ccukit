"""The core to read labber hdf file. By Neuro Sama :)

"""

import numpy as np
import h5py
from decimal import Decimal

__all__ = [
    'LabberHDF',
]

class LabberHDF:
    """ The object to read labber measured data, the hfd5 file.

    Attributes:
        traces_map : dict[int, str]
            The map from interger to trace name.
        instconfig_map : dict[int, str]
            The map from interger to instrument config name.
        stepconfig_map : dict[int, dict]
            The map from interger to step config dictionary.

    Methods:
        overvirew(self) -> None:
            print an overview of the file.
        get_trace_by_index(self, index) -> ndarray:
            Get trace data as an ndarray, using `traces_map` indexing.
        get_instconfig_by_index(self, index) -> dict:
            Get instrument config as a dictionary, using `instconfig_map` indexing.
        get_stepconfig_by_index(self, index) -> dict:
            Get step config as a dictionary, using `stepconfig_map` indexing.
    """

    def __init__(self, filepath:str, *, print_traces_map: bool=False):
        self.filepath = filepath
        # traces (contains dataset)
        self.traces_map: dict[int, str] = self._get_int2name_map(
            groupname='Traces',
            print_keys=print_traces_map
        )
        # instrument configs (contains dataset)
        self.instconfig_map: dict[int, str] = self._get_int2name_map(
            groupname='Instrument config'
        )
        # Step configs (contains group)
        self.stepconfig_map: dict[int, dict]= self._get_int2name_map(
            groupname='Step config'
        )
        #
        self.steplist_dict = self._get_step_list_dict()

    def _get_int2name_map(self, groupname, print_keys=False) -> dict:
        """ Return a dictionary that maps int -> str. \
            Where int is from 0~n, \
            str is datates names under the group `groupname`."""
        temp = {}
        with h5py.File(self.filepath, 'r') as f:
            for index, key in enumerate(f[groupname].keys()):
                if print_keys: print(f'{index} : {key}')
                temp[index] = key
        return temp

    
    def _get_reevaluated_step_item(self, step_item_dict, relparm_dict, stepconfig_groupname):
        """ reevaluate step item, for Labber only make a portion of step item is correct,\
            e.g. when range_type is 'start-stop', only 'start' and 'stop' value are coorect.
            This function reevaluate the step items into more convinient and reable one.
        """
        result_dict = {}

        use_relation = self.steplist_dict[stepconfig_groupname]['use_relations']
        if use_relation:
            eqation = self.steplist_dict[stepconfig_groupname]['equation']
            var_sym = relparm_dict['variable']
            var_name = relparm_dict['channel_name']
            result_dict['range_type'] = 'Follow'
            result_dict['follow'] = f'{eqation}, {var_sym} = {var_name}'
        else:
            range_type = step_item_dict['range_type']
            step_type = step_item_dict['step_type']
            if range_type == 'Single':
                result_dict['range_type'] = 'Single'
                result_dict['single'] = step_item_dict['single']
                result_dict['start'] = step_item_dict['single']
                result_dict['stop'] = step_item_dict['single']
                result_dict['center'] = step_item_dict['single']
                result_dict['span'] = 0
                result_dict['step'] = 0
                result_dict['n_pts'] = 1
            else:
                result_dict['range_type'] = 'Sweep'
                if range_type == 'Start - Stop':
                    start = Decimal( str(step_item_dict['start']) )
                    stop = Decimal( str(step_item_dict['stop']) )
                    result_dict['start'] = float(start)
                    result_dict['stop'] = float(stop)
                    result_dict['center'] = float((start + stop) / 2)
                    result_dict['span'] = float(abs(stop - start))
                    span = Decimal( str(result_dict['span']) ) # for step use
                if range_type == 'Center - Span': 
                    center = Decimal( str(step_item_dict['center']) )
                    span = Decimal( str(step_item_dict['span']) ) # also for step use
                    result_dict['start'] = float(center - span/2)
                    result_dict['stop'] = float(center + span/2)
                    result_dict['center'] = float(center)
                    result_dict['span'] = float(span)

                
                if step_type == 'Fixed step':
                    result_dict['step'] = step_item_dict['step']
                    result_dict['n_pts'] = int(round( float(span) / result_dict['step'])) + 1
                if step_type == 'Fixed # of pts':
                    result_dict['n_pts'] = int(step_item_dict['n_pts'])
                    result_dict['step'] = float( float(span) / (result_dict['n_pts']-1) )
        return result_dict

    def _get_step_list_dict(self) -> dict:
        with h5py.File(self.filepath, 'r') as f:
            dataset = f['Step list']
            fields = dataset.dtype.names 
            values = dataset
            
            result_dict = {}
            for i in range(values.shape[0]):
                indiviual_dict = {}
                for field in fields:
                    value = values[field][i]
                    if type(value) == bytes:
                        value = value.decode('utf-8')
                    indiviual_dict[field] = value
                result_dict[indiviual_dict['channel_name']] = indiviual_dict

        return result_dict
    def overview(self, print_option='111') -> None:
        """ For nth digit of print option string: 1th -> trace, \
            2nd -> instrument config, 3rd -> step config. 1 to print, \
            0 for don't print. 
        """
        if int(str(print_option)[0]):
            print('Traces:')
            for index, name in self.traces_map.items():
                print(f'{index} : {name}')
            print('----------')
        if int(str(print_option)[1]):
            print('instrument config:')
            for index, name in self.instconfig_map.items():
                print(f'{index} : {name}')
            print('----------')
        if int(str(print_option)[2]):
            print('step config:')
            for index, name in self.stepconfig_map.items():
                print(f'{index} : {name}')
            print('----------')

    def get_trace_by_name(self, name:str) ->  np.ndarray:
        with h5py.File(self.filepath, 'r') as f:
            """ Return trace data by given name."""
            return np.array(f['Traces'][name])
    def get_trace_by_index(self, index: int) -> np.ndarray:
        """ Return trace data by index, according to mapping in dict `traces_ds_map`."""
        with h5py.File(self.filepath, 'r') as f:
            return np.array(f['Traces'][self.traces_map[index]])
        

    def get_instconfig_by_index(self, index: int) -> dict:
        """ Return trace data by index, according to mapping in dict `instconfig_ds_map`."""
        with h5py.File(self.filepath, 'r') as f:
            return dict(f['Instrument config'][self.instconfig_map[index]].attrs)
    def get_instconfig_by_name(self, name: str) -> dict:
        """ Return trace data by index, according to mapping in dict `instconfig_ds_map`."""
        with h5py.File(self.filepath, 'r') as f:
            return dict(f['Instrument config'][name].attrs)       
    
    def get_stepconfig_by_name(self, name: str, reevaluate=True) -> dict:
        def get_key_by_value(dictionary, target_value):
            return next((key for key, value in dictionary.items() if value == target_value), -1)
        index = get_key_by_value(self.stepconfig_map, name)
        if index == -1:
            raise Exception('No such step config name') from None
        else:
            return self.get_stepconfig_by_index(index, reevaluate)
    def get_stepconfig_by_index(self, index: int, reevaluate=True) -> dict:
        """ Return trace data by index, according to mapping in dict `instconfig_ds_map`."""
        with h5py.File(self.filepath, 'r') as f:
            stepconfig_groupname = self.stepconfig_map[index]

            # toss Optimizer since it is not valid outside Labber logbrowser
            stepconfig_dict = {'Step items': None, 'Relation parameters': None}
            
            #### Construct Step items dictionary
            enum_mapping = {
                "range_type": {0: "Single", 1: "Start - Stop", 2: "Center - Span"},
                "step_type": {0: "Fixed step", 1: "Fixed # of pts"},
            }
            # read raw step item into a dictionary
            dataset = f['Step config'][stepconfig_groupname]['Step items']
            fields = dataset.dtype.names 
            values = dataset
            stepitem_dict = {field: float(values[field][0]) for field in fields}
            # convert enum to string
            for key in ['range_type', 'step_type']:
                enum_value = stepitem_dict[key]
                stepitem_dict[key] = enum_mapping[key][enum_value]
            # done

            #### Construct Relation parameters dictionary
            dataset = f['Step config'][stepconfig_groupname]['Relation parameters']
            fields = dataset.dtype.names
            values = dataset
            relparm_dict = {field: values[field][0] for field in fields}

            if type(relparm_dict['variable']) == bytes:
                relparm_dict['variable'] = relparm_dict['variable'].decode('utf-8')
            if type(relparm_dict['channel_name']) == bytes:
                relparm_dict['channel_name'] = relparm_dict['channel_name'].decode('utf-8')
            
            relparm_dict['use_lookup'] = bool(relparm_dict['use_lookup'])
            # done

            if reevaluate:
                stepitem_dict = self._get_reevaluated_step_item(
                    stepitem_dict, relparm_dict, stepconfig_groupname
                )
            stepconfig_dict['Step items'] = stepitem_dict
            stepconfig_dict['Relation parameters'] = relparm_dict
            return stepconfig_dict