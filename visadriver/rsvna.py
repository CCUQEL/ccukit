"""The high level control objects that warps visa layers to control R&SVNA. By Neuro Sama :)


"""

from pyvisa.resources import Resource
import numpy as np
from time import sleep

__all__ = [
    'RSVNA',
]

class RSVNA:
    """The high level KeySight EXG control object by Tasi14. 
    
    Example usage and adresses:
    >>> import pyvisa
    >>> from ccukit.visadriver import RSVNA
    >>> rm = pyvisa.ResourceManager()
    >>> vna = RSVNA('VNA', rm.open_resource('TCPIP0::192.168.1.4::INSTR'))
    
    The * in the docstring below means they are commonly used ones.

    Attributes:
    -- id: the id of the R&S VNA.
    -- visa_resource: the visa resource of the R&S VNA.
    -- sparm_channel_map: a dictionary that maps s parameter to channel names.

    Setter like method:
    -- visa_write: write SCPI command to R&S VNA.
    -- clear_error_flag: clear error flag of R&S VNA.
    *- s_parm_enabled: set Snm (S11, S21 etc) to be enable or disable.
    *- output: set output to 'ON' or 'OFF'.
    *- power: set the output power, in dBm.
    *- freq_start_stop: set the sweeping frequency by start-stop.
    *- freq_center_span: set the sweeping frequency by center-span.
    *- n_pts: set the number of points.
    *- n_avg: set the number of avarge, 0 for not averaging.

    Getter like method:
    -- visa_query: write SCPI command to R&S VNA, return the response.
    *- get_trace_data: get trace data for Snm (S11, S21 etc).
    -- get_trace_data_currently: Get trace data of current ONLY measurement. (lagcy)
    
    """
    # RSVNA_resource.query(...):
    # *IDN?  ->  get device informatiom
    
    # RSVNA_resource.write(...):
    # *CLS  ->  clear the state (also error flag)
    

    def __init__(self, id: str, visa_resource: Resource) -> None:
        self.id = id
        self.visa_resource = visa_resource
        self.sparm_channels_map: dict[str, list[str]] = {}

    def update_sparm_channels_map(self):
        """
        This method of acess S parameter names and storage is copied from Labber driver for R&S VNA.
        """
        self.sparm_channels_map = {}
        parmcat = self.visa_query("CALC:PAR:CAT?")[1:-2] # get rid of ' and \n
        items = parmcat.split(',') # e.g. 'CH4TR1,S11,CH4TR2,S12'
        n_measurements = len(items) // 2
        for n in range(n_measurements):
            channel_name = items[2*n] # e.g. 'CH4TR1', 'CH4TR2'
            s_parm = items[2*n + 1]   # e.g. 'S11', 'S12'
            if s_parm not in self.sparm_channels_map:
                # create list with current name
                self.sparm_channels_map[s_parm] = [channel_name,]
            else:
                # add to existing list
                self.sparm_channels_map[s_parm].append(channel_name)


    #### setter like method
    def visa_write(self, command):
        """write SCPI command to R&S VNA."""
        self.visa_resource.write(command)
    def clear_error_flag(self):
        """clear error flag of R&S VNA."""
        self.visa_resource.write('*CLS')
    def output(self, on_or_off: str):
        """ON or OFF."""
        self.visa_resource.write(f":OUTP {on_or_off}")
    def power(self, power: float):
        """set output power, in dBm. Available: "TO BE FILLED IN"."""
        self.visa_resource.write(
            f":SOUR:POW {power}"
        )
    def if_bandwidth(self, if_bandwidth):
        """set the if bandwidth. 10kHz is default for VNA."""
        self.visa_write(f":SENS:BWID {if_bandwidth}")
    def freq_start_stop(self, freq_start: float, freq_stop):
        """set sweep frequency by start-stop."""
        self.visa_write(f":SENS:FREQ:STAR {freq_start}")
        self.visa_write(f":SENS:FREQ:STOP {freq_stop}")
    def freq_center_span(self, freq_center: float, freq_span):
        """set sweep frequency by center-span."""
        self.visa_write(f":SENS:FREQ:CENT {freq_center}")
        self.visa_write(f":SENS:FREQ:SPAN {freq_span}")
    def n_pts(self, n_pts: int):
        """set number of swpped frequency points."""
        self.visa_write(f":SENS:SWE:POIN {int(n_pts)}")
    def n_avg(self, n_avg: int):
        """set number of aveage, 0 for not avaeageing."""
        if n_avg == 0:
            self.visa_write(f":SENS:AVER:COUN 1")
            self.visa_write(f":SENS:AVER 0")
        else:
            self.visa_write(f":SENS:AVER:COUN {int(n_avg)}")
            self.visa_write(f":SENS:AVER 1")

    def s_parm_enabled(self, s_parm_str: str, enabled: bool):
        """set Snm to be enable, like S11, S21 etc.
        
        Example usage:
        >>> vna.s_parm_enabled('S11', True)
        >>> vna.s_parm_enabled('S21', False)
        """
        self.update_sparm_channels_map()
        # create new measurement, is enable is true
        if enabled:
            new_name = 'LabC_%s' % s_parm_str
            self.visa_write(f"CALC:PAR:SDEF '{new_name}','{s_parm_str}'")
            # show on PNA screen
            iTrace = 1 + [
                'S11', 'S12', 'S13', 'S14', 
                'S21', 'S22', 'S23', 'S24', 
                'S31', 'S32', 'S33', 'S34', 
                'S41', 'S42', 'S43', 'S44'
            ].index(s_parm_str)
            self.visa_write(f"DISP:WIND:TRAC{iTrace}:FEED '{new_name}'")
        # delete the measurment is enable is false, and it is currently enabled
        if not enabled:
            if s_parm_str in self.sparm_channels_map:
                for name in self.sparm_channels_map[s_parm_str]:
                    self.visa_write(f"CALC:PAR:DEL '{name}'")
        self.update_sparm_channels_map()

    #### getter like method
    def visa_query(self, command):
        """write SCPI command to keysight EXG, return the response."""
        return self.visa_resource.query(command)
    def get_freqs(self):
        """Get sweeped frequencies"""
        fstart = float(self.visa_query(":SENS:FREQ:STAR?"))
        fstop = float(self.visa_query(":SENS:FREQ:STOP?"))
        n_pts = int(self.visa_query(":SENS:SWE:POIN?"))
        return np.linspace(fstart, fstop, n_pts)
    def get_output_status(self):
        states_str = self.visa_query(':OUTP?')
        if states_str == '1\n': return 'ON'
        elif states_str == '0\n': return 'OFF'

    def measure_trace(self, s_parm_str: str, python_avg=True) -> np.ndarray:
        """Get trace data for S parameter measurement, empty array for not measureing.
        
        Args:
            s_parm_str (string): S parameter to be measured. 'S11', 'S12', 'S21', 'S22' etc.
            python_avg (bool): default is true, use VNA setting to do average in python, see doc.

        Explanation:
            In newer version of VNA, it has no funtionality to obtain current process of 
            averaged trace, so I consult the value mutiple times to simulate the avarge
            in this code. Another approach is to approximate the time it tooks and use sleep.
            If anyone have a better approach, please fix this.

        Example usage:
        >>> s21 = vna.get_trace_data('S21')
        >>> freq = vna.get_freqs()
        >>> plt.plot(freq, np.abs(s21))
        """
        # update the currentlt measuring quantites, return empy array for not measureing
        self.update_sparm_channels_map()
        if s_parm_str not in self.sparm_channels_map:
            return np.array([])

        # get channel name for this measurement and set it to focus for VNA
        channel_name = self.sparm_channels_map[s_parm_str][-1] # get last active channel
        self.visa_write(f"CALC:PAR:SEL '{channel_name}'")
        
        if python_avg and self.visa_query(':SENS:AVER?') == '1\n':
            n_avg = int(self.visa_query(':SENS:AVER:COUN?'))
        else:
            n_avg = 1

        cont_avg_v_complex = np.zeros(int(self.visa_query(':SENS:SWE:POIN?')))
        for sweep_no in range(1, n_avg+1):
            # 1. switch to single sweep mode, 2. restart a sweep,  3. wait for it to complete
            self.visa_write(':ABOR;:INIT:CONT OFF;:INIT:IMM;*OPC')
            sweep_finished = False
            while not sweep_finished:
                sleep(0.05)
                stb = int(self.visa_query('*ESR?'))
                sweep_finished = (stb & 1) > 0

            # consult s parameter value. 
            # This method of low level acess is copied from Labber driver for R&S VNA
            self.visa_write(':FORM REAL,32')
            self.visa_resource.write("CALC:DATA? SDATA")
            raw_data = self.visa_resource.read_raw()
            self.visa_write('*CLS;:INIT:CONT ON;') # turn VNA back to continous sweeping mode. 

            # convert raw data to measurment values
            # This method of low level acess is copied from Labber driver for R&S VNA
            i0 = raw_data.find(b'#')
            n_dig = int(raw_data[i0+1 : i0+2])
            n_byte = int(raw_data[i0+2 : i0+2 + n_dig])
            n_data = int(n_byte/4)
            n_pts = int(n_data/2)
            v_data = np.frombuffer(
                raw_data[(i0+2 + n_dig) : (i0+2 + n_dig + n_byte)], 
                dtype='>f', count=n_data)
            v_data_2col = v_data.reshape((n_pts, 2)) # data is in "I0, Q0, I1, Q1, I2, Q2, .." format
            v_complex = v_data_2col[:, 0] + 1j*v_data_2col[:, 1]

            # continuous avarging
            cont_avg_v_complex = (cont_avg_v_complex*(sweep_no-1) + v_complex) / sweep_no

        return cont_avg_v_complex
    
    def get_trace_data_currently(self, suppress_warn=False) -> np.ndarray:
        """Get trace data of current ONLY measurement. (lagcy)"""
        if self.get_output_status() == 'OFF':
            if not suppress_warn:
                print('warning: output is off, the value is not formatted corretly.')

        parcat = self.visa_query('CALC:PAR:CAT?')[1:-2] # get rid of ' and \n
        if parcat == '':
            raise Exception('No measurements is on VNA now')
        channel_name = parcat.split(',')[0] # get first channel name
        s_name = parcat.split(',')[1] # get first s name
        self.visa_write(f"CALC:PAR:SEL '{channel_name}'")
        
        # this method of low level acess is copied from Labber driver for R&S VNA
        self.visa_write(':FORM REAL,32')
        self.visa_resource.write("CALC:DATA? SDATA")
        raw_data = self.visa_resource.read_raw()
        i0 = raw_data.find(b'#')
        n_dig = int(raw_data[i0+1 : i0+2])
        n_byte = int(raw_data[i0+2 : i0+2 + n_dig])
        n_data = int(n_byte/4)
        n_pts = int(n_data/2)
        v_data = np.frombuffer(
            raw_data[(i0+2 + n_dig) : (i0+2 + n_dig + n_byte)], 
            dtype='>f', count=n_data)
        v_data_2col = v_data.reshape((n_pts, 2)) # data is in "I0, Q0, I1, Q1, I2, Q2, .." format
        v_complex = v_data_2col[:, 0] + 1j*v_data_2col[:, 1]
        return v_complex