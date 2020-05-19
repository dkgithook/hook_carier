#!/usr/bin/python3
# coding=utf-8
# pylint: disable=I0011

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
    Base64 config seed
"""

import base64

from dusty.models.seed import SeedModel


class Seed(SeedModel):
    """ Base64 config seed class """

    def handle(self, config_seed_data):
        """ Unseed config from seed, return None on error """
        return base64.b64decode(config_seed_data)

    @staticmethod
    def get_name():
        """ Module name """
        return "base64"

    @staticmethod
    def get_description():
        """ Module description or help message """
        return "Base64 seed"
