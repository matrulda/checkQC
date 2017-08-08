
from math import pow

from checkQC.handlers.qc_handler import QCHandler, QCErrorWarning, QCErrorFatal
from checkQC.parsers.stats_json_parser import StatsJsonParser


class YieldHandler(QCHandler):

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None
        self.qc_config = qc_config

    def parser(self):
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):

        for lane_dict in self.conversion_results:
            lane_nbr = lane_dict["LaneNumber"]
            lane_yield = lane_dict["Yield"]

            if lane_yield < float(self.qc_config["error"]) * pow(10, 9):
                yield QCErrorFatal("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            elif lane_yield < float(self.qc_config["warning"]) * pow(10, 9):
                yield QCErrorWarning("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            else:
                continue

