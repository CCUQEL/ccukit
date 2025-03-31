"""The high level control objects that warps visa layers to control R&SVNA. By Neuro Sama :)


"""

from pyvisa.resources import Resource
import numpy as np
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
    
    Setter like method:
    -- visa_write: write SCPI command to R&S VNA.
    -- reset: reset the VNA settings.
    *- enable_snm: set Snm to be enable, like S11, S21 etc.
    *- disable_snm: set Snm to be disable, like S11, S21 etc.
    *- output: set output to 'ON' or 'OFF'.
    *- power: set the output power, in dBm.
    *- freq_start_stop: set the sweeping frequency by start-stop.
    *- freq_center_span: set the sweeping frequency by center-span.
    *- n_pts: set the number of points.
    *- n_avg: set the number of avarge, 0 for not averaging.

    Getter like method:
    -- visa_query: write SCPI command to R&S VNA, return the response.
    *- get_trace_data: get trace data for current view.
    
    """
    # RSVNA_resource.query(...):
    # *IDN?  ->  get device informatiom
    
    # RSVNA_resource.write(...):
    # *CLS  ->  clear the state (also error flag)
    

    def __init__(self, id: str, visa_resource: Resource) -> None:
        self.id = id
        self.visa_resource = visa_resource

    #### setter like method
    def visa_write(self, command):
        """write SCPI command to R&S VNA."""
        self.visa_resource.write(command)
    def reset(self):
        """Reset the VNA."""
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
            self.visa_write(f":SENS:AVER 0")
        else:
            self.visa_write(f":SENS:AVER:COUN {int(n_avg)}")
            self.visa_write(f":SENS:AVER 1")

    # def enable_snm(self, s_name: str):
    #     """set Snm to be enable, like S11, S21 etc."""
    #     param = s_name
    #     self.getActiveMeasurements()
    #     # clear old measurements for this parameter
    #     if param in self.dMeasParam:
    #         for name in self.dMeasParam[param]:
    #             self.writeAndLog("CALC:PAR:DEL '%s'" % name)
    #     # create new measurement,
    #     newName = 'LabC_%s' % param
    #     self.visa_write("CALC:PAR:SDEF '%s','%s'" % (newName, param))
    #     # show on PNA screen
    #     iTrace = 1 + [
    #         'S11', 'S12', 'S13', 'S14', 
    #         'S21', 'S22', 'S23', 'S24', 
    #         'S31', 'S32', 'S33', 'S34', 
    #         'S41', 'S42', 'S43', 'S44'
    #     ].index(param)
    #     self.visa_write("DISP:WIND:TRAC%d:FEED '%s'" % (iTrace, newName))
    #     # add to dict with list of measurements
    #     self.dMeasParam[param] = [newName]




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

    def get_trace_data(self, suppress_warn=False):
        """Get trace data of current ONLY setting."""
        if self.get_output_status() == 'OFF':
            if not suppress_warn:
                print('warning: output is off, the value is not formatted corretly.')

        # now only support getting one trace, so it grab the first one
        parcat = self.visa_query('CALC:PAR:CAT?')[1:-2] # get rid of ' and \n
        channel_name = parcat.split(',')[0] # get first channel name
        s_name = parcat.split(',')[1] # get first s name
        self.visa_write(f"CALC:PAR:SEL '{channel_name}'")
        
        # this method of low level acess is copied from Labber driver for R&S VNA
        self.visa_write(':FORM REAL,32')
        self.visa_resource.write("CALC:DATA? SDATA")
        raw_data = self.visa_resource.read_raw()
        i0 = raw_data.find(b'#')
        nDig = int(raw_data[i0+1:i0+2])
        nByte = int(raw_data[i0+2:i0+2+nDig])
        nData = int(nByte/4)
        nPts = int(nData/2)
        # get data to numpy array
        vData = np.frombuffer(raw_data[(i0+2+nDig):(i0+2+nDig+nByte)], 
                                dtype='>f', count=nData)
        # data is in I0,Q0,I1,Q1,I2,Q2,.. format, convert to complex
        mC = vData.reshape((nPts,2))
        vComplex = mC[:,0] + 1j*mC[:,1]
        return vComplex