import interop
import csv
import pathlib

from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

class QCData:
    def __init__(
        self,
        instrument,
        read_length,
        samplesheet,
        lane_data,  # TODO validate dict content
        # The schema will define mandatory fields but may evolve over time with
        # new instruments
        # TODO find better name?
    ):
        self.instrument = instrument
        self.read_length = read_length
        self.samplesheet = samplesheet
        self.lane_data = lane_data

    from checkQC.parsers.illumina import from_bclconvert

    from checkQC.views.illumina import illumina_view

    def report(self, config):
        # TODO select correct config based on read_len and instrument
        # TODO make sure default_handlers are included
        # TODO add optional parameter to select closest read length
        # TODO validate config with schema
        #   - schema could be dynamic, i.e. we add the handlers named allowed
        #   based on the methods defined in QCData

        qc_reports = [
            qc_report
            for handler_config in config["handlers"]
            for qc_report in getattr(self, handler_config["name"])(**handler_config)
            # TODO is it ok if method name don't follow snake_case? Should we have a method
            # to convert the name to snake_case? And maybe remove handler too?
        ]

        return getattr(self, config.get("view", "illumina_view"))(qc_reports)

    def ErrorRateHandler(self, error, warning, allow_missing_error_rate): # Should this be just `error_rate`
        assert error > warning
        # TODO impl. allow_missing_error_rate

        return [
            QCErrorFatal("Error: ErrorRateHandler", data={"lane": lane, "read": read})
            if read_data["mean_error_rate"] > error else
            QCErrorWarning("Warning: ErrorRateHandler", data={"lane": lane, "read": read})
            for lane, lane_data in self.lane_data.items()  # TODO find better name for lane_data
            for read, read_data in lane_data["reads"].items()
            if read_data["mean_error_rate"] > warning
        ]
