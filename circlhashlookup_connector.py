#!/usr/bin/env python3

# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import phantom.app as phantom
import requests
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector


BASE_URL = "https://hashlookup.circl.lu"
REQUEST_TIMEOUT = 30

# Hash length: (CIRCL URL name, CIRCL response field)
HASH_TYPES = {
    32: ("md5", "MD5"),
    40: ("sha1", "SHA-1"),
    64: ("sha256", "SHA-256"),
}


class RetVal(tuple):
    def __new__(cls, status, data=None):
        return tuple.__new__(cls, (status, data))


class CirclHashLookupConnector(BaseConnector):
    def __init__(self):
        super().__init__()
        self._state = None
        self._base_url = BASE_URL

    def _make_rest_call(self, endpoint, action_result):
        config = self.get_config()

        try:
            response = requests.get(
                self._base_url + endpoint,
                headers={"Accept": "application/json"},
                timeout=REQUEST_TIMEOUT,
                verify=config.get("verify_server_cert", True),
            )
        except requests.exceptions.RequestException as exc:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"Error connecting to CIRCL: {exc!s}",
                )
            )

        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": response.status_code})
            action_result.add_debug_data({"r_text": response.text})
            action_result.add_debug_data({"r_headers": dict(response.headers)})

        content_type = response.headers.get("Content-Type", "").lower()

        # A lookup that returns 404 completed successfully but found no record.
        if response.status_code == 404 and endpoint.startswith("/lookup/") and "json" in content_type:
            return RetVal(phantom.APP_SUCCESS, None)

        try:
            response_data = response.json()
        except ValueError:
            response_text = response.text.replace("{", "{{").replace("}", "}}")
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"CIRCL returned HTTP {response.status_code}: {response_text}",
                )
            )

        if 200 <= response.status_code < 300:
            return RetVal(phantom.APP_SUCCESS, response_data)

        response_text = response.text.replace("{", "{{").replace("}", "}}")
        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR,
                f"CIRCL returned HTTP {response.status_code}: {response_text}",
            )
        )

    def _handle_test_connectivity(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))
        self.save_progress("Connecting to CIRCL hashlookup")

        ret_val, response = self._make_rest_call("/info", action_result)
        if phantom.is_fail(ret_val):
            self.save_progress("Test Connectivity Failed")
            return action_result.get_status()

        if not isinstance(response, dict) or "stat:hashlookup_total_keys" not in response:
            return action_result.set_status(
                phantom.APP_ERROR,
                "CIRCL returned an unexpected response from /info.",
            )

        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(
            phantom.APP_SUCCESS,
            "Successfully connected to CIRCL hashlookup.",
        )

    def _handle_file_reputation(self, param):
        action_result = self.add_action_result(ActionResult(dict(param)))

        hash_value = param.get("hash")
        if not isinstance(hash_value, str):
            return action_result.set_status(phantom.APP_ERROR, "The hash must be a string.")

        hash_value = hash_value.strip().lower()
        hash_info = HASH_TYPES.get(len(hash_value))

        if hash_info is None or any(character not in "0123456789abcdef" for character in hash_value):
            return action_result.set_status(
                phantom.APP_ERROR,
                "Enter a valid hexadecimal MD5, SHA-1, or SHA-256 hash.",
            )

        hash_type, response_hash_field = hash_info
        self.save_progress(f"Looking up {hash_type.upper()} hash in CIRCL")

        endpoint = f"/lookup/{hash_type}/{hash_value}"
        ret_val, response = self._make_rest_call(endpoint, action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        if response is None:
            action_result.update_summary({"hash": hash_value, "hash_type": hash_type, "found": False})
            return action_result.set_status(
                phantom.APP_SUCCESS,
                "Hash not found in CIRCL hashlookup.",
            )

        if not isinstance(response, dict) or str(response.get(response_hash_field, "")).lower() != hash_value:
            return action_result.set_status(
                phantom.APP_ERROR,
                "CIRCL returned an unexpected lookup response.",
            )

        action_result.add_data(response)
        summary = action_result.update_summary({"hash": hash_value, "hash_type": hash_type, "found": True})

        for response_field, summary_field in {
            "FileName": "file_name",
            "FileSize": "file_size",
            "source": "source",
            "db": "database",
            "hashlookup:trust": "trust_score",
        }.items():
            value = response.get(response_field)
            if value is not None:
                summary[summary_field] = value

        return action_result.set_status(
            phantom.APP_SUCCESS,
            "Hash found in CIRCL hashlookup.",
        )

    def handle_action(self, param):
        action_id = self.get_action_identifier()
        self.debug_print("action_id", action_id)

        if action_id == "file_reputation":
            return self._handle_file_reputation(param)
        if action_id == "test_connectivity":
            return self._handle_test_connectivity(param)

        return phantom.APP_ERROR

    def initialize(self):
        self._state = self.load_state()
        return phantom.APP_SUCCESS

    def finalize(self):
        self.save_state(self._state)
        return phantom.APP_SUCCESS
