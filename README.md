# CIRCL Hash Lookup

Publisher: Arminius Technologies LLC <br>
Connector Version: 1.0.0 <br>
Product Vendor: Arminius Technologies LLC <br>
Product Name: CIRCL Hash Lookup <br>
Minimum Product Version: 7.4.0

This app allows the leveraging CIRCL hash look up database

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration <br>
[file reputation](#action-file-reputation) - Queries for file reputation info

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** <br>
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'file reputation'

Queries for file reputation info

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**hash** | required | File hash to query | string | `hash` `sha256` `sha1` `md5` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.hash | string | `hash` `sha256` `sha1` `md5` | |
action_result.status | string | | |
action_result.message | string | | |
summary.total_objects | numeric | | |
action_result.data.\*.parents.\*.PackageDescription | string | | |
action_result.data.\*.PackageDescription | string | | |
action_result.data.\*.hashlookup:trust | string | | |
action_result.data.\*.source | string | | |
summary.total_objects_successful | numeric | | |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
