"""
This file defines the FIR filter class.

This class is used to organize the characteristics of the filter


"""

class FIR_Filter:
    def __init__(self, taps, dequantization_params) -> None:
        self.taps = taps
        self.num_taps = len(taps)
        self.dq_params = dequantization_params
        return
    