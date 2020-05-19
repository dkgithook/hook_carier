#!/usr/bin/python3
# coding=utf-8
# pylint: skip-file

#   Copyright 2019 getcarrier.io
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
    Code from Dusty 1.0
"""

import traceback

from time import time
from reportportal_client import ReportPortalServiceAsync as ReportPortalService

from . import constants # from dusty import constants

rp_service = None


def timestamp():
    return str(int(time() * 1000))


def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    traceback.print_exception(*exc_info)


def launch_reportportal_service(rp_config):
    if not rp_config:
        return None
    global rp_service

    if not rp_service:
        rp_service = ReportPortalDataWriter(endpoint=rp_config["rp_url"],
                                            token=rp_config["rp_token"],
                                            project=rp_config["rp_project"],
                                            launch_name=rp_config["rp_launch_name"],
                                            tags=rp_config["rp_launch_tags"])
        rp_service.start_test()
    return rp_service


class ReportPortalDataWriter:
    def __init__(self, endpoint, token, project, log_batch_size=100, launch_name=None, tags=None,
                 launch_doc=None, launch_id=None, verify_ssl=False):
        self.endpoint = endpoint
        self.token = token
        self.project = project
        self.log_batch_size = log_batch_size
        self.launch_name = launch_name
        self.tags = tags
        self.launch_doc = launch_doc
        self.service = None
        self.test = None
        self.verify_ssl = verify_ssl
        self.launch_id = launch_id

    def start_service(self):
        self.service = ReportPortalService(endpoint=self.endpoint,
                                           project=self.project,
                                           token=self.token,
                                           log_batch_size=self.log_batch_size,
                                           verify_ssl=self.verify_ssl)
        if self.launch_id:
            self.service.launch_id = self.launch_id

    def start_test(self):
        if not self.service:
            self.start_service()
        return self.service.start_launch(name=self.launch_name,
                                         start_time=timestamp(),
                                         description=self.launch_doc,
                                         tags=self.tags)

    def finish_test(self):
        self.service.finish_launch(end_time=timestamp())
        self.service.terminate()
        self.service = None

    def is_test_started(self):
        if self.service:
            return True
        return False

    def start_test_item(self, issue, description, tags, item_type='STEP', parameters={}):
        self.service.start_test_item(issue, description=description,
                                     tags=tags, start_time=timestamp(),
                                     item_type=item_type, parameters=parameters)

    def test_item_message(self, message, level="ERROR", attachment=None):
        if len(message) > constants.MAX_MESSAGE_LEN:
            index = 0
            while index < len(message):
                increment = constants.MAX_MESSAGE_LEN
                if index + increment > len(message):
                    increment = len(message) - index
                self.service.log(time=timestamp(), message=message[index:index+increment],
                                 level=level, attachment=attachment)
                index = index+increment
        else:
            self.service.log(time=timestamp(), message=message,
                             level=level, attachment=attachment)

    def finish_test_item(self, status="FAILED"):
        self.service.finish_test_item(end_time=timestamp(),
                                      status=status)
