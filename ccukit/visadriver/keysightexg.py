"""The high level control objects that warps visa layers to control KeySightEXG. By Neuro Sama :)


"""

from pyvisa.resources import Resource
__all__ = [
    'KeySightEXG',
]

class KeySightEXG:
    """The high level KeySight EXG control object by Tasi14. 
    
    Example usage and adresses:
    >>> import pyvisa
    >>> from ccukit.visadriver import KeySightEXG
    >>> rm = pyvisa.ResourceManager()
    >>> rf1 = KeySightEXG('RF1', rm.open_resource('TCPIP0::192.168.1.5::INSTR'))
    
    The * in the docstring below means they are commonly used ones.

    Attributes:
    -- id: the id of the keysight EXG.
    -- visa_resource: the visa resource of the keysight EXG.
    
    Setter like method:
    -- visa_write: write SCPI command to keysight EXG.
    -- clear_error_flag: clear the error flag on keysight EXG.
    *- output: set output to 'ON' or 'OFF'.
    *- power: set the output power, in dBm.
    *- freq: set the output frequency, in Hz.

    Getter like method:
    -- visa_query: write SCPI command to keysight EXG, return the response.
    -- get_output_status: get output states, 'ON' or 'OFF'.
    -- get_power: get output power, in dBm.
    -- get_freq: get output frequency, in Hz.

    """
    # keysightEXG_resource.query(...):
    # *IDN?  ->  get device informatiom
    
    # keysightEXG_resource.write(...):
    # *CLS  ->  clear the state (also error flag)
    
    # both (add `?` to query):
    # :OUTP (ON|OFF)|?  ->  0(1) for output is off(on)
    # :SOUR:FREQ (freq)|?  ->  output frequency
    # :SOUR:POW:IMM:AMPL (amp)|?  ->  output power
    # :SOUR:PHAS:ADJ (phase)|?  ->  output phase
    # :POW:ALC (0|1)|? -> automatic level controlling
    # :UNIT:POW (V|DBM)|? -> power unit

    def __init__(self, id: str, visa_resource: Resource) -> None:
        self.id = id
        self.visa_resource = visa_resource
        visa_resource.write(':POW:ALC 1') # automatic level controlling
        visa_resource.write(':UNIT:POW DBM') # power unit

    #### setter like method
    def visa_write(self, command):
        """write SCPI command to keysight EXG."""
        self.visa_resource.write(command)
    def clear_error_flag(self):
        """clear the error flag on keysight EXG."""
        self.visa_resource.write('*CLS')
    def output(self, on_or_off: str):
        """ON or OFF."""
        self.visa_resource.write(f":OUTP {on_or_off}")
    def power(self, power: float):
        """set output power, in dBm. Available: -20dBm ~ 19dBm."""
        self.visa_resource.write(
            f":SOUR:POW:IMM:AMPL {power}"
        )
    def freq(self, freq: float):
        """set output frequency, in Hz. Available: 9kHz ~ 13GHz."""
        self.visa_resource.write(f":SOUR:FREQ {freq}")

    #### getter like method
    def visa_query(self, command):
        """write SCPI command to keysight EXG, return the response."""
        return self.visa_resource.query(command)
    def get_output_status(self) -> str:
        """get output states, 'ON' or 'OFF'."""
        states_str = self.visa_query(':OUTP?')
        if states_str == '1\n': return 'ON'
        elif states_str == '0\n': return 'OFF'
    def get_power(self) -> float:
        """get output power, in dBm"""
        return float(self.visa_query(':SOUR:POW:IMM:AMPL?'))
    def get_freq(self) -> float:
        """get output frequency, in Hz"""
        return float(self.visa_query(':SOUR:FREQ?'))
