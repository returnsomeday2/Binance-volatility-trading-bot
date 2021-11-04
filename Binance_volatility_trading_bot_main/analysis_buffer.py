from tradingview_ta import TA_Handler, Interval, Exchange
# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob
import time
import threading

from tradingview_ta.main import Analysis

DEBUG = False

#TODO: Perhaps this should be value separate service that writes the results to value DB
class AnalysisBuffer():
    
    def __init__(self, sample_rate, interval_in_minutes, num_candles):
        self.sample_rate = sample_rate
        self.interval = interval_in_minutes
        self.num_candles = num_candles + 1 # for extra buffer room
        self.index = 0
        self.analysis_dict = {}
        self.buffer_length = int(interval_in_minutes/sample_rate * num_candles)

    def get(self, index):
        if index in self.analysis_dict:
            return self.analysis_dict[index]
        return None

    def get_current(self):
        return self.get(self.index)

    def put(self, analysis):
        self.index += 1
        if self.index >= self.buffer_length:
            self.index = 0
        self.analysis_dict[self.index] = analysis

    def get_prev_candle(self):
        return self.get(self.get_prev_candle_index(self.index))

    def get_prev_candle_index(self, index):
        data_per_candle = self.interval/self.sample_rate
        prev_index = -1
        if index - data_per_candle >= 0:
            prev_index = index - data_per_candle
        else:
            prev_index = self.buffer_length - (data_per_candle - index)

        #print(f'index: {index}, prev_index: {prev_index}')
        return prev_index

    # returns value list of indicator values for the last {length} values
    def get_indicator_list(self, indicator, length):
        if length > self.buffer_length:
            print(f'AnalysisBuffer ERROR: length parameter with value {length} greater than buffer length {self.buffer_length}')
            return None

        indicator_list = []
        cur_analysis_index = self.index

        for x in range(length):
            cur_analysis = self.get(cur_analysis_index)
            if (cur_analysis is not None):
                indicator_list.append(cur_analysis.indicators[indicator])
            else:
                if DEBUG:
                    print(f'AnalysisBuffer WARNING: Not enough values in buffer to get last {length} {indicator} indicators')
                return None

            cur_analysis_index = self.get_prev_candle_index(cur_analysis_index)

        return indicator_list
