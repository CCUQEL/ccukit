"""The high level control objects that warps visa layers to control YOKOGAWA. By Neuro Sama :)


"""

from pyvisa.resources import Resource
import numpy as np
import time
from typing import List, Tuple
import threading

__all__ = [
    'YOKOGAWA',
]


class YOKOGAWA:
    """The high level yokogawa control object by Tasi14. 
    
    Example usage and adresses:
    >>> import pyvisa
    >>> from tsai14 import YOKOGAWA
    >>> rm = pyvisa.ResourceManager()
    >>> yoko1 = YOKOGAWA('DC1', rm.open_resource('USB0::0x0B21::0x0039::90ZC38697::0::INSTR'))
    >>> yoko2 = YOKOGAWA('DC2', rm.open_resource('USB0::0x0B21::0x0039::90ZC38696::0::INSTR'))
    >>> yoko3 = YOKOGAWA('DC3', rm.open_resource('USB0::0x0B21::0x0039::9017D5818::0::INSTR'))
    >>> yoko4 = YOKOGAWA('DC4', rm.open_resource('USB0::0x0B21::0x0039::9017D5816::0::INSTR'))
    
    The * in the docstring below means they are commonly used ones.

    Attribute:
    -- name: name of the YOKOGAWA.
    -- visa_resource: visa resource object.
    
    Setter like method:
    -- visa_write: write SCPI command to yokogawa.
    -- clear_error_flag: turn off the error led on yokogawa.
    -- operation_setting: set 'CURR'/'VOLT' mode and range.
    *- output: set output to 'ON' or 'OFF'.
    *- output_value: set the output value, in unit of V or A.
    *- sweep: sweep from current value to goal value.

    Getter like method:
    -- visa_write: write SCPI command to yokogawa, return the response.
    -- get_operation_setting: get current operation setting.
    -- get_output_states: get the output states, 'ON' or 'OFF'.
    -- get_output_value: get the output value, in unit of V or A.
    
    Static method:
    -- demag_single: run demag script for a single YOKOGAWA.
    *- demag: run demag script for mutiple YOKOGAWAs.
    *- wait_for_sweeping: wait for all the YOKOGAWAs to finish sweeping.
    """
    # yoko_resource.query(...):
    # *IDN?  ->  get device informatiom

    # yoko_resource.write(...):
    # *CLS  ->  clear the state (also error flag)

    # both (add `?` to query):
    # :OUTP (ON|OFF)|?  ->  0(1) for output is off(on)
    # :SOUR:FUNC (VOLT|CURR)|?  ->  voltage or current supply mode.
    # :SOUR:RANGE (value)|?  ->  source range
    # :SOUR:LEV (value)|?  ->  source level
    def __init__(self, id: str, visa_resource: Resource) -> None:
        self.id = id
        self.visa_resource = visa_resource

    #### setter like method
    def visa_write(self, command):
        """write SCPI command to yokogawa."""
        self.visa_resource.write(command)
    def clear_error_flag(self):
        """turn off the error led light on yokogawa."""
        self.visa_write('*CLS')
    def operation_setting(self, func: str, range: float):
        """specify function and range.

            func:
                current supply: CURR.
                voltage supply: VOLT.

            range (in unit of V or A):
                VOLT: 30, 10, 1, 100e-3, 10e-3.
                CURR: 200e-3, 100e-3, 10e-3, 1e-3.
            
            resulution (correspond to each range):
                VOLT: 1e-3, 100e-6, 10e-6, 1e-6, 100e-9.
                CURR: 1e-6, 1e-6, 100e-9, 10e-9.
        """
        self.visa_write(
            f":SOUR:FUNC {func}; RANG {range}"
        )
    def output(self, on_or_off: str):
        """set output by 'ON' or 'OFF'."""
        self.visa_write(f":OUTP {on_or_off}")
    def output_value(self, value: float):
        """set output source level, in unit of V or A."""
        self.visa_write(f":SOUR:LEV {value}")
    def sweep(self, 
              goal_value, 
              delta_time, 
              delta_value, 
        ) -> threading.Thread:
        """sweep from current value to goal value, in unit of V or A, in a new thread. See docstring. 
        
        The sweeping will be excute in a new thread immedately and it returns the thread object,
        user can use thread.join() to block excuation.
        Example usage:
        >>> yoko1.sweep(200e-3, 0.1, 10e-3) # it will NOT wait for sweeping
        >>> yoko2.sweep(100e-3, 0.1, 10e-3).join() # it WILL wait for sweeping
        
        User can also use the static method `wait_for_sweeping` to wait for all sweeping to finish.
        Example usage:
        >>> YOKOGAWA.wait_for_sweeping(
                yoko1.sweep(200e-3, 0.1, 10e-3),
                yoko2.sweep(200e-3, 0.1, 10e-3)
                yoko3.sweep(50e-3,  0.1, 10e-3)
            )
        >>> # Thie line will be arrived after all DCs finished sweeping.
        """
        def inner(goal_value, delta_time, delta_value):
            curr_value = self.get_output_value()
            if goal_value < curr_value:
                delta_value = -delta_value
            source_levels = np.arange(curr_value, goal_value, delta_value)
            for level in source_levels:
                self.output_value(level)
                time.sleep(delta_time)
            time.sleep(delta_time)
            self.output_value(goal_value)
        
        # open new thread and start immediately
        thread = threading.Thread(
            target=inner, args=(goal_value, delta_time, delta_value) 
        )
        thread.start()
        return thread

    #### getter like method
    def visa_query(self, command):
        """write SCPI command to yokogawa, return the response."""
        return self.visa_resource.query(command)
    def get_operation_setting(self) -> Tuple[str, float]:
        """get current operation setting. 'VOLT' or 'CURR', and range."""
        func = self.visa_query(':SOUR:FUNC?')[:-1]
        range = float(self.visa_query(':SOUR:RANG?'))
        return func, range
    def get_output_status(self) -> str:
        """get output states, 'ON' or 'OFF'."""
        states_str = self.visa_query(':OUTP?')
        if states_str == '1\n': return 'ON'
        elif states_str == '0\n': return 'OFF'
    def get_output_value(self) -> float:
        """get output source level, in unit of V or A."""
        return float(self.visa_query(':SOUR:LEV?'))

    #### static methods
    @staticmethod
    def wait_for_sweeping(*threads: List[threading.Thread]):
        """Used to write docstring like code, wait threads of sweeping to finished.

        Example usage:
        >>> YOKOGAWA.wait_for_sweeping(
                yoko1.sweep(200e-3, 0.1, 10e-3),
                yoko2.sweep(200e-3, 0.1, 10e-3)
                yoko3.sweep(50e-3,  0.1, 10e-3)
            )
        >>> # Thie line will be arrived after all DCs finished sweeping."""
        for thread in threads:
            thread.join()
    @staticmethod
    def demag_single(yoko: "YOKOGAWA", path: list, sweep_delta_time=0.05, sweep_delta_current=2e-3):
        """Run demag script for a single YOKOGAWA.
        It go through all the point in the `path`, by sweeping.
        """
        for point in path:
            yoko.sweep(point, sweep_delta_time, sweep_delta_current).join()
    @staticmethod
    def demag(yokos: List["YOKOGAWA"], path: list, sweep_delta_time=0.05, sweep_delta_current=2e-3):
        """Run demag script for mutiple YOKOGAWAs."""
        threads = []
        for yoko in yokos:
            threads.append(threading.Thread( 
                target=YOKOGAWA.demag_single, args=(yoko, path, sweep_delta_time, sweep_delta_current) 
                ))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()



