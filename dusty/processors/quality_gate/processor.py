#!/usr/bin/python3
# coding=utf-8

#   Copyright 2020 getcarrier.io
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Processor: quality_gate
"""

from ruamel.yaml.comments import CommentedMap  # pylint: disable=E0401

from dusty.tools import log
from dusty.models.module import DependentModuleModel
from dusty.models.processor import ProcessorModel
from dusty.constants import SEVERITIES


class Processor(DependentModuleModel, ProcessorModel):
    """ Process quality gate """

    def __init__(self, context):
        """ Initialize processor instance """
        super().__init__()
        self.context = context
        self.config = \
            self.context.config["processing"][__name__.split(".")[-2]]

    def execute(self):
        """ Run the processor """
        log.info("Checking quality gate status")
        thresholds = self.config.get("thresholds", dict())
        # Count issues by severity
        results_by_severity = dict()
        for item in self.context.findings:
            if item.get_meta("information_finding", False) or \
                    item.get_meta("false_positive_finding", False) or \
                    item.get_meta("excluded_finding", False):
                continue
            severity = item.get_meta("severity", SEVERITIES[-1])
            if severity not in results_by_severity:
                results_by_severity[severity] = 0
            results_by_severity[severity] += 1
        # Prepare stats data
        stats_data = dict()
        for severity in SEVERITIES:
            stats_data["total"] = "OK"
            stats_data[severity] = {
                "findings": results_by_severity.get(severity, "-"),
                "threshold": thresholds.get(severity, "-"),
                "status": "OK"
            }
        # Check quality gate
        for severity in results_by_severity:
            if severity not in thresholds:
                continue
            #
            severity_results = results_by_severity[severity]
            policy_threshold = thresholds[severity]
            #
            if severity_results > policy_threshold:
                log.warning(
                    "Quality gate failed: %s -> %d > %d",
                    severity, severity_results, policy_threshold
                )
                self.context.set_meta("fail_quality_gate", True)
                stats_data[severity]["status"] = "FAIL"
                stats_data["total"] = "FAIL"
        # Prepare stats
        stats = list()
        stats.append("============= Quality gate stats ============")
        stats.append("Severity  : {:<9} {:<5} {:<7} {:<4} {:<4}".format(
            *SEVERITIES
        ))
        stats.append("Findings  : {:<9} {:<5} {:<7} {:<4} {:<4}".format(
            *[stats_data[severity]["findings"] for severity in SEVERITIES]
        ))
        stats.append("Threshold : {:<9} {:<5} {:<7} {:<4} {:<4}".format(
            *[stats_data[severity]["threshold"] for severity in SEVERITIES]
        ))
        stats.append("Status    : {:<9} {:<5} {:<7} {:<4} {:<4}".format(
            *[stats_data[severity]["status"] for severity in SEVERITIES]
        ))
        stats.append("============= Quality gate: {:<4} ============".format(stats_data["total"]))
        self.context.set_meta("quality_gate_stats", stats)

    @staticmethod
    def fill_config(data_obj):
        """ Make sample config """
        data_obj.insert(
            len(data_obj), "thresholds", CommentedMap(),
            comment="Quality gate thresholds by severity"
        )
        mapping_obj = data_obj["thresholds"]
        mapping_obj.insert(
            len(mapping_obj),
            "Critical", 3
        )
        mapping_obj.insert(
            len(mapping_obj),
            "High", 5
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Medium", 7
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Low", 9
        )
        mapping_obj.insert(
            len(mapping_obj),
            "Info", 11
        )

    @staticmethod
    def run_after():
        """ Return optional depencies """
        return ["exclude_by_endpoint", "false_positive", "min_severity_filter"]

    @staticmethod
    def get_name():
        """ Module name """
        return "Quality gate"

    @staticmethod
    def get_description():
        """ Module description """
        return "Set and check quality gate for CI/CD process"
