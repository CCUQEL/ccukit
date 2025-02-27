"""The single purpose module for exepriment of VNA with a DC supply sweep. By Neuro Sama :)

"""

from .core import LabberHDF
import numpy as np
from matplotlib import pyplot as plt
from numbers import Number

__all__ = [
    'VNAxDC',
]

class VNAxDC:
    """An object to read expeiment data stored by labber, for VNA with a DC sweep setup
    
    Attributes:
    -- filepath : str, The path to the file.
    -- file : LabberHDF, The object to read labber measured data, the hfd5 file.
    -- info : dict, The dictionary contains information about measurment, e.g. n_pts, startf, stopf etc...
    -- vna_traces : ndarray, The array contains VNA traces data.
    -- freq: ndarray, The array of VNA sweeped frequency.
    -- curr: ndarray, The array of DC supply sweeped current.
    
    Methods:
    -- get_traces_cut: Get a cut of trace base on icut, fcut.
    -- debackground: Return debackgrounded VNA traces data. optinally to create new hdf5 file.
    -- get_2dploting_objs: Returns fig, ax, extent, flipfunc. See doc for detail
    """
    dc_supply_no = ['1', '2', '3', '4', '5', '6']
    possible_traces = [
        'S11', 'S12', 'S13', 'S14',
        'S21', 'S22', 'S23', 'S24',
        'S31', 'S32', 'S33', 'S34',
        'S41', 'S42', 'S43', 'S44',
    ]
    def __init__(self, filepath: str, print_info=False) -> None:
        self.filepath = filepath
        self.file = LabberHDF(filepath)
        self.info = self._get_info(print_info=print_info)
        self.vna_traces = self._get_vna_traces()
        
        # find sweeping frequency
        startf = self.info['VNA - start frequency']
        stopf = self.info['VNA - stop frequency']
        f_pts = self.info['VNA - # of points']
        self.freq_sweep = np.linspace(startf, stopf, f_pts)

        # find sweeping current (if any)
        sweeping_dc_no = self.info.get('Sweeping DC no', None)
        if sweeping_dc_no is not None:
            starti = self.info[f'DC{sweeping_dc_no} - start current']
            stopi = self.info[f'DC{sweeping_dc_no} - stop current']
            i_pts = self.info['VNA - # of traces']
            self.curr_sweep = np.linspace(starti, stopi, i_pts)

            # Check whether the sweep quantity is flipped, for 2d plot
            self._iflip, self._fflip = False, False
            if starti > stopi:
                self._iflip = True
            if startf > stopf:
                self._fflip = True
            
            

    def _get_info(self, print_info = False):
        """Get informations about measurment, e.g. n_pts, startf, stopf etc... .
        
        Argumenumt
        ----------
        file : LabberHDF
            The LabberHDF file object.
        print_info : bool, optioanl
            Default is False, print the obtained values.
        
        Return
        ----------
        info : dictionary
            A dictionary contains information about measurment, see code for details.
        """
        info = {}
        # NVA: Find which trace it has measured
        trace = ''
        for trial_trace in VNAxDC.possible_traces:
            if f'VNA - {trial_trace}' in self.file.traces_map.values():
                trace = trial_trace
                break
        if trace == '':
            raise Exception('No VNA trace found')
        info['VNA - trace'] = trace
        # NVA: Get number of traces, points; start, stop frequency
        vna_traces = self.file.get_trace_by_name(f'VNA - {trace}')
        npts = vna_traces.shape[0]
        ntrc = vna_traces.shape[2]
        startf, stepf = self.file.get_trace_by_name(f'VNA - {trace}_t0dt')[0, :]
        stopf = startf + stepf * (npts-1)
        info['VNA - # of points'] = npts
        info['VNA - # of traces'] = ntrc
        info['VNA - start frequency'] = startf
        info['VNA - stop frequency'] = stopf
        info['VNA - frequency step'] = stepf
        
        # DC: find which dc supply is used and sweeping
        for no in VNAxDC.dc_supply_no:
            name = f'DC supply - {no} - Current'
            if name in self.file.stepconfig_map.values():
                stepconfig = self.file.get_stepconfig_by_name(name)
                step_item = stepconfig['Step items']
                if step_item['range_type'] == 'Single':
                    info[f'DC{no} - sweep'] = False
                    info[f'DC{no} - current'] = step_item['single']
                if step_item['range_type'] == 'Follow':
                    info[f'DC{no} - sweep'] = False
                    info[f'DC{no} - current'] = step_item['follow']
                if step_item['range_type'] == 'Sweep':
                    info[f'DC{no} - sweep'] = True
                    info[f'DC{no} - start current'] = step_item['start']
                    info[f'DC{no} - stop current'] = step_item['stop']
                    info[f'DC{no} - # of steps'] = step_item['n_pts']
                    info[f'DC{no} - current step'] = step_item['step']
                    info[f'Sweeping DC no'] = no
        if print_info:
            for key, value in info.items():
                print(key, ':', value)
        return info

    def _get_vna_traces(self):
        """ Get data of VNA traces.

        Return
        ----------
        NVA_traces: ndarray
            2d complex data, measured by VNA.
        """
        trace = self.info['VNA - trace']
        vna_traces_raw = self.file.get_trace_by_name(f'VNA - {trace}')
        vna_traces = vna_traces_raw[:, 0, :] + vna_traces_raw[:, 1, :]*1j
        return vna_traces
    

    def debackground(self, bg_filepath: str, mode:str = '/', create_file=False) -> np.ndarray:
        """Add an hdf5 file for debackground data that log browser can open.

        bg_filepath: str
            The background file path.
        mode: str, optional
            Support `-` or `/`, the debackground method. However, we believe `/`
            is the coorect method.
        create_file: bool, optional
            If true, it creats a copy of `data_filepath` with _debg appended, with debg data.
        """

        bg_trace = VNAxDC(bg_filepath).vna_traces
        extended_bg = bg_trace * np.ones_like(self.vna_traces)
        if mode == '-':
            is_snn = self.info['VNA - trace'][1] == self.info['VNA - trace'][2]
            if is_snn:
                debg_vna_traces = self.vna_traces - extended_bg
            else:
                # If you don't know why there are 1+, you are soooo stupid
                debg_vna_traces = 1 + self.vna_traces - extended_bg
        elif mode == '/':
            debg_vna_traces = self.vna_traces / extended_bg
        
        if create_file:
            import os
            import shutil
            def append_debackground_to_file_path(file_path: str) -> str:
                base_path, filename = os.path.split(file_path)
                filename_without_extension, file_extension = os.path.splitext(filename)
                new_filename = f"{filename_without_extension}_debg{file_extension}"
                new_file_path = os.path.join(base_path, new_filename)
                return new_file_path
            # creat a new file and write debackground data
            trace = self.info['VNA - trace']
            debg_filepath = append_debackground_to_file_path(self.filepath)
            shutil.copyfile(self.filepath, debg_filepath)
            import h5py
            with h5py.File(debg_filepath, 'r+') as f:
                # labber uses float16 to store data, np uses float128 by default
                f['Traces'][f'VNA - {trace}'][:, 0, :] = np.real(debg_vna_traces).astype(np.float16)
                f['Traces'][f'VNA - {trace}'][:, 1, :] = np.imag(debg_vna_traces).astype(np.float16)
            print(f'Debackground file is creared at : "{debg_filepath}"')
        
        return debg_vna_traces
    
    def i2ind(self, current):
        no = self.info['Sweeping DC no']
        i0 = self.info[f'DC{no} - start current']
        i1 = self.info[f'DC{no} - stop current']
        stepi = self.info[f'DC{no} - current step']
        if (current < i0 and current < i1) or\
        (current > i0 and current > i1):
            raise Exception(
                f'specified current `{current}` is out of range' ) from None
        return int(round( (current - i0)/stepi))
    def f2ind(self, freq):
        f0 = self.info['VNA - start frequency']
        f1 = self.info['VNA - stop frequency']
        nf = self.info['VNA - # of points']
        stepf = (f1 - f0) / nf
        if (freq < f0 and freq < f1) or\
        (freq > f0 and freq > f1):
            raise Exception(
                f'specified frequency `{freq}` is out of range' ) from None
        return int(round( (freq - f0) / stepf))


    def get_traces_cut(self, 
                       icut, 
                       fcut=None) -> tuple:
        """ Get a cut of trace base on icut, fcut. Also return current and frequency.

        Arguments:
        -- icut : the current to cut, in unit of Ampere.
        -- fcut : the frequency to cut, in unit of Hz.
        If cut is None, it'll show whole range, if it's a number, it'll cut single
        trace out as 1d array. If it is [lower, upper] list, it'll return a 2d array.

        Returns:
        -- cutted_freq : ndarray
        -- cutted_current : ndarray
        -- cutted_trace : ndarray

        Example usage:
        >>> cutted_freq, cutted_current, cutted_trace = exp1.get_traces_cut(icut = 50e-3)
        >>> cutted_freq, cutted_current, trace_detail = exp1.get_traces_cut(icut = 50e-3, fcut = [3e+9, 4e+9])

        """
        flipfunc = self._get_flip_func(transpose=False)
        # whole range for i
        if icut == None:
            i_acceeser = slice(None, None)
        # single f trace
        elif isinstance(icut, Number):
            i_ind = self.i2ind(icut)
            i_acess_ind = (self.info['VNA - # of traces'] - 1) - i_ind
            i_acceeser = i_acess_ind
        # mutiple f traces
        else:
            i0_ind = self.i2ind(icut[0])
            i1_ind = self.i2ind(icut[1])
            i0_acess_ind = (self.info['VNA - # of traces'] - 1) - i0_ind
            i1_acess_ind = (self.info['VNA - # of traces'] - 1) - i1_ind
            if i0_acess_ind > i1_acess_ind:
                i0_acess_ind, i1_acess_ind = i1_acess_ind, i0_acess_ind
            i_acceeser = slice(i0_acess_ind, i1_acess_ind)

        # whole range for f
        if fcut == None:
            f_acceeser = slice(None, None)
        # single i trace
        elif isinstance(fcut, Number):
            f_ind = self.f2ind(fcut)
            f_acceeser = f_ind
        # mutiple i traces
        else:
            f0_ind = self.f2ind(fcut[0])
            f1_ind = self.f2ind(fcut[1])
            if f0_ind > f1_ind:
                f0_ind, f1_ind = f1_ind, f0_ind
            f_acceeser = slice(f0_ind, f1_ind)

        if self._fflip:
            cutted_freq = np.flip(self.freq_sweep)[f_acceeser]
        else:
            cutted_freq = self.freq_sweep[f_acceeser]
        if not self._iflip:
            cutted_current = np.flip(self.curr_sweep)[i_acceeser]
        else:
            cutted_current = self.curr_sweep[i_acceeser]

        return cutted_freq, cutted_current, flipfunc(self.vna_traces)[i_acceeser, f_acceeser]

    def get_2dploting_objs(self, transpose = True):
        """ Return figure, axes, extent that auto sets based on `info`. use plt.imshow() to plot.

        usage example:
        >>> traces = exp.vna_traces
        >>> fig, ax, extend, flipfunc = exp1.get_2dploting_objs()
        >>> plt.imshow(
        >>>     flipfunc(np.abs(traces)), 
        >>>     aspect='auto',
        >>>     extent=extend,
        >>>     vmin=0, vmax=1,
        >>>     cmap='viridis_r',
        >>> )
        >>> plt.colorbar().set_label(exp.info['VNA - trace'])
        >>> plt.show()

        Arguments
        ----------
        transpose: optional, default is True
            If true, the VNA frequency will be on y axis instead of x axis.
        
        Returns
        ----------
        fig: matplotlib.figure.Figure
            The figure object.
        ax: matplotlib.axes.Axes
            The axes object.
        extend: list
            used as and argument of plt.imshow().
        flipfunc: function
            Apply to VNA_trace data to print it correctly.
        """
        # Gather nessesay informations
        startf = self.info['VNA - start frequency']
        stopf = self.info['VNA - stop frequency']
        trace = self.info['VNA - trace']
        dc_no = self.info['Sweeping DC no']
        starti = self.info[f'DC{dc_no} - start current']
        stopi = self.info[f'DC{dc_no} - stop current']
    
        # cearting fig and ax and apply settings
        fig, ax = plt.subplots()
        if not self._fflip: f0, f1 = startf, stopf
        else: f0, f1 = stopf, startf
        if not self._iflip: i0, i1 = starti, stopi
        else: i0, i1 = stopi, starti
        if transpose:
            extent = [i0*1e3, i1*1e3, f0/1e9, f1/1e9]
            ax.set_title(trace)
            ax.set_xlabel(f'DC{dc_no} current / mA')
            ax.set_ylabel('VNA frequency / GHz')
        else:
            extent = [f0/1e9, f1/1e9, i0*1e3, i1*1e3]
            ax.set_title(trace)
            ax.set_ylabel(f'DC{dc_no} current / mA')
            ax.set_xlabel('VNA frequency / GHz')

        flipfunc = self._get_flip_func(transpose=transpose)
        return fig, ax, extent, flipfunc
    
    def _get_flip_func(self, transpose):
        def flipfunc(data):
            """flip the data to plot correctly
            
            We often make a plot that x and y axis that acceding from left to right
            and from bottom to up. However, the data is stored in an array from
            left to right and from up to down, so we need to flip axis 0.

            Futuremore, if our measurment swpeed the quantity from large to small,
            the stored data will be flipped again, so we need to flip the correpond
            axis, in order to make a plot we want.

            If we make the plot transpose, then not only we transpose the data, we need 
            to oppsite the flip rule for x and y axis.
            """
            if transpose:
                if not self._fflip:
                    data = np.flip(data, axis=0)
                if self._iflip:
                    data = np.flip(data, axis=1)
            if not transpose:
                data = data.T
                if self._fflip:
                    data = np.flip(data, axis=1)
                if not self._iflip:
                    data = np.flip(data, axis=0)
            return data
        return flipfunc