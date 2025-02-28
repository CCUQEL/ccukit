"""The module to read general experiment with SA and a sweeping quantity (SAxANY)

"""

from .core import LabberHDF
import numpy as np
from matplotlib import pyplot as plt
from numbers import Number

__all__ = [
    'SAxANY',
]

class SAxANY:
    """An object to read expeiment data stored by labber, for SA with any ohter is sweeping.
    
    It supports to read file without sweep quantity, but many functionality will not supported then.

    Attributes:
    -- filepath : str, The path to the file.
    -- file : LabberHDF, The object to read labber measured data, the hfd5 file.
    -- info : dict, The dictionary contains information about measurmen.
    -- sa_traces : ndarray, The array contains SA traces data.
    -- freq_sweep: ndarray, The array of SA swpped frequency.
    -- s_sweep: ndarray, The array of sweeped quantity other then SA.
    
    Methods:
    -- get_traces_cut: Get a cut of trace base on scut, fcut.
    -- debackground: Return debackgrounded SA traces data. optinally to create new hdf5 file.
    -- get_2dploting_objs: Returns fig, ax, extent, flipfunc. See doc for detail
    """
    def __init__(self, filepath: str, 
                 print_info=False,
        ) -> None:
        self.filepath = filepath
        self.file = LabberHDF(filepath)
        self.info = self._get_info(print_info=print_info)
        self.sa_traces = self._get_sa_traces()
        
        # for sweeping frequency
        startf = self.info['SA - start frequency']
        stopf = self.info['SA - stop frequency']
        f_pts = self.info['SA - # of points']
        self.freq_sweep = np.linspace(startf, stopf, f_pts)

        # for other sweeping quantity, if any
        if self.info['sweep - name'] is not None:
            starts = self.info['sweep - start']
            stops = self.info['sweep - stop']
            s_pts = self.info['SA - # of traces']
            self.s_sweep = np.linspace(starts, stops, s_pts)

            # Check whether the sweep quantity is flipped, for 2d plot
            self._sflip, self._fflip = False, False
            if starts > stops:
                self._sflip = True
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
        # SA: Get number of traces, points; start, stop frequency
        sa_traces = self.file.get_trace_by_name('SA - Signal')
        npts = sa_traces.shape[0]
        ntrc = sa_traces.shape[2]
        startf, stepf = self.file.get_trace_by_name('SA - Signal_t0dt')[0, :]
        stopf = startf + stepf * (npts-1)
        info['SA - # of points'] = npts
        info['SA - # of traces'] = ntrc
        info['SA - start frequency'] = startf
        info['SA - stop frequency'] = stopf
        info['SA - frequency step'] = stepf
        
        # ANY: find sweeping quantity
        sweepings = []
        for index, name in self.file.stepconfig_map.items():
            stepconfig = self.file.get_stepconfig_by_name(name)
            if stepconfig['Step items']['range_type'] == 'Sweep':
                sweepings.append((name, stepconfig))
        if len(sweepings) == 0: 
            info['sweep - name'] = None
        elif len(sweepings) == 1:
            sweeping_name, sweeping_stepconfig = sweepings[0]
            info['sweep - name'] = sweeping_name
            info['sweep - start'] = sweeping_stepconfig['Step items']['start']
            info['sweep - stop'] = sweeping_stepconfig['Step items']['stop']
            info['sweep - step'] = sweeping_stepconfig['Step items']['step']
            # n_pts can be find as info['SA - # of traces']
        else:
            raise Exception(
                f'Only support 1 sweeping quantity, however there are {len(sweepings)}.'
            ) from None

        if print_info:
            for key, value in info.items():
                print(key, ':', value)
        return info

    def _get_sa_traces(self):
        """ Get data of SA traces.

        Return
        ----------
        sa_traces: ndarray
            2d data, measured by SA, the PSD has magnitude only.
        """
        sa_traces_raw = self.file.get_trace_by_name('SA - Signal')
        sa_traces = sa_traces_raw[:, 0, :]
        return sa_traces
    
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

        bg_trace = SAxANY(bg_filepath).sa_traces
        extended_bg = bg_trace * np.ones_like(self.sa_traces)
        if mode == '-':
            is_snn = self.info['SA - trace'][1] == self.info['SA - trace'][2]
            if is_snn:
                debg_sa_traces = self.sa_traces - extended_bg
            else:
                # If you don't know why there are 1+, you are soooo stupid
                debg_sa_traces = 1 + self.sa_traces - extended_bg
        elif mode == '/':
            debg_traces = self.sa_traces / extended_bg
        
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
            trace = self.info['SA - trace']
            debg_filepath = append_debackground_to_file_path(self.filepath)
            shutil.copyfile(self.filepath, debg_filepath)
            import h5py
            with h5py.File(debg_filepath, 'r+') as f:
                # labber uses float16 to store data, np uses float128 by default
                f['Traces']['SA - Signal'][:, 0, :] = debg_traces.astype(np.float16)
            print(f'Debackground file is creared at : "{debg_filepath}"')
        
        return debg_traces
    
    def s2ind(self, s_value):
        if self.info['sweep - name'] is None:
            raise Exception("s2ind not supported for data without sweep quantity.")

        s0 = self.info['sweep - start']
        s1 = self.info['sweep - stop']
        steps = self.info['sweep - step']
        if (s_value < s0 and s_value < s1) or\
        (s_value > s0 and s_value > s1):
            raise Exception(
                f'specified value `{s_value}` is out of range' ) from None
        return int(round( (s_value - s0)/steps))
    def f2ind(self, freq):
        f0 = self.info['SA - start frequency']
        f1 = self.info['SA - stop frequency']
        nf = self.info['SA - # of points']
        stepf = (f1 - f0) / nf
        if (freq < f0 and freq < f1) or\
        (freq > f0 and freq > f1):
            raise Exception(
                f'specified frequency `{freq}` is out of range' ) from None
        return int(round( (freq - f0) / stepf))

    def get_traces_cut(self, 
                       scut=None, 
                       fcut=None) -> tuple:
        """ Get a cut of trace base on scut, fcut. Also return current and frequency.

        Arguments:
        -- scut : the sweeping quantity to cut, unit is the same as what Labber sets.
        -- fcut : the frequency to cut, in unit of Hz.
        If cut is None, it'll show whole range, if it's a number, it'll cut single
        trace out as 1d array. If it is [lower, upper] list, it'll return a 2d array.

        Returns:
        -- cutted_freq : ndarray
        -- cutted_s : ndarray
        -- cutted_trace : ndarray

        Example usage:
        >>> cutted_freq, cutted_s, cutted_trace = exp1.get_traces_cut(scut = 50e-3)
        >>> cutted_freq, cutted_s, trace_detail = exp1.get_traces_cut(scut = 50e-3, fcut = [3e+9, 4e+9])

        """
        if self.info['sweep - name'] is None:
            raise Exception("get_traces_cut not supported for data without sweep quantity.")
        
        flipfunc = self._get_flip_func(transpose=False)
        # whole range for s
        if scut == None:
            s_acceeser = slice(None, None)
        # single f trace
        elif isinstance(scut, Number):
            s_ind = self.s2ind(scut)
            s_acess_ind = (self.info['SA - # of traces'] - 1) - s_ind
            s_acceeser = s_acess_ind
        # mutiple f traces
        else:
            s0_ind = self.s2ind(scut[0])
            s1_ind = self.s2ind(scut[1])
            s0_acess_ind = (self.info['SA - # of traces'] - 1) - s0_ind
            s1_acess_ind = (self.info['SA - # of traces'] - 1) - s1_ind
            if s0_acess_ind > s1_acess_ind:
                s0_acess_ind, s1_acess_ind = s1_acess_ind, s0_acess_ind
            s_acceeser = slice(s0_acess_ind, s1_acess_ind)

        # whole range for f
        if fcut == None:
            f_acceeser = slice(None, None)
        # single s trace
        elif isinstance(fcut, Number):
            f_ind = self.f2ind(fcut)
            f_acceeser = f_ind
        # mutiple s traces
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
        if not self._sflip:
            cutted_current = np.flip(self.s_sweep)[s_acceeser]
        else:
            cutted_current = self.s_sweep[s_acceeser]

        return cutted_freq, cutted_current, flipfunc(self.sa_traces)[s_acceeser, f_acceeser]

    def get_2dploting_objs(self, transpose = True):
        """ Return figure, axes, extent that auto sets based on `info`. use plt.imshow() to plot.

        usage example:
        >>> traces = exp1.sa_traces
        >>> fig, ax, extend, flipfunc = exp1.get_2dploting_objs()
        >>> plt.imshow(
        >>>     flipfunc(traces), 
        >>>     aspect='auto',
        >>>     extent=extend,
        >>>     # vmin=-120, vmax=-10,
        >>>     cmap='inferno',
        >>> )
        >>> plt.colorbar().set_label('PSD / (A.U.)')
        >>> plt.show()

        Arguments
        ----------
        transpose: optional, default is True
            If true, the SA frequency will be on y axis instead of x axis.
        
        Returns
        ----------
        fig: matplotlib.figure.Figure
            The figure object.
        ax: matplotlib.axes.Axes
            The axes object.
        extend: list
            used as and argument of plt.imshow().
        flipfunc: function
            Apply to SA_trace data to print it correctly.
        """
        if self.info['sweep - name'] is None:
            raise Exception("get_2dploting_objs is not supported for data without sweep quantity.")

        # Gather nessesay informations
        startf = self.info['SA - start frequency']
        stopf = self.info['SA - stop frequency']
        sname = self.info['sweep - name']
        starts = self.info['sweep - start']
        stops = self.info['sweep - stop']
    
        # cearting fig and ax and apply settings
        fig, ax = plt.subplots()
        if not self._fflip: f0, f1 = startf, stopf
        else: f0, f1 = stopf, startf
        if not self._sflip: s0, s1 = starts, stops
        else: s0, s1 = stops, starts
        if transpose:
            extent = [s0, s1, f0/1e9, f1/1e9]
            ax.set_title('SA')
            ax.set_xlabel(sname)
            ax.set_ylabel('SA frequency / GHz')
        else:
            extent = [f0/1e9, f1/1e9, s0, s1]
            ax.set_title('SA')
            ax.set_ylabel(sname)
            ax.set_xlabel('SA frequency / GHz')

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
                if self._sflip:
                    data = np.flip(data, axis=1)
            if not transpose:
                data = data.T
                if self._fflip:
                    data = np.flip(data, axis=1)
                if not self._sflip:
                    data = np.flip(data, axis=0)
            return data
        return flipfunc