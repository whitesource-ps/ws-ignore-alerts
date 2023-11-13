![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-ignore-alerts)](https://github.com/whitesource-ps/ws-ignore-alerts/releases/latest) 
[![WS Ignore Alerts Build and Publish](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml)
[![Python 3.6](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Blue_Python_3.6%2B_Shield_Badge.svg/86px-Blue_Python_3.6%2B_Shield_Badge.svg.png)](https://www.python.org/downloads/release/python-360/)

# Ignore Future Alerts 
**ws_ignore_alerts.py** is a utility for automated ignoring alerts in the newly created WS project, which is a version of the same customer's product,
according to the previously ignored alerts in the baseline WS project. Once a new UA scan has finished, and a new project has been created, 
the utility can be launched as part of the pipeline for automated ignoring alerts.
There are three options for use:
- using a baseline project token and destination project name defined by the user - baselineProjectToken and destProjectName (optional: destProjectVersion). Might work with different products.
- using a baseline project token and destination project token defined by the user - baselineProjectToken and destProjectToken. Might work with different products.
- using the default behavior, without providing baseline and destination projects' data. In this case, the destination project is a latest project of the certain product and baseline project is one before the latest project of the same product. Only works within a certain product.
The ignored alerts will be pulled from the baseline project, and the same alerts will be ignored in the destination project.

### Supported Operating Systems
- Linux (Bash): CentOS, Debian, Ubuntu, RedHat
- Windows (PowerShell): 10, 2012, 2016

### Prerequisites
- Python 3.7 or above ([additional prerequisites](https://wiki.python.org/moin/WindowsCompilers) might be required when using Microsoft Windows)

## Installation and Execution from PyPi:
1. Install by executing: `pip install ws-ignore-alerts`
2. Configure the appropriate parameters either by using the command line or in `params.config`.
3. Execute the tool (`ws_ignore_alerts ...`).

## Installation and Execution from GitHub:
1. Download and unzip **ws-ignore-alerts.zip**
2. Install requirements: `pip install -r requirements.txt`
3. Configure the appropriate parameters either by using the command line or `params.config`.
4. Execute: `python ignore_alerts.py`

### Execution Examples
From the command line:
- `python ws_ignore_alerts.py -u $wsUrl -k $userKey -o $orgToken -p $productToken -b $baselineProjectToken -n 
  $destProjectName -v $destProjectVersion -t $destProjectToken -d $destProductToken -w whitelist.txt`
or
- `python ws_ignore_alerts.py -u $wsUrl -k $userKey -o $orgToken -p $productToken -b $baselineProjectToken -n 
  $destProjectName -v $destProjectVersion -t $destProjectToken -d $destProductToken -w CVE-xxxx-yyyy,CVE-zzzz-tttt`

Using a config file:
- `python ws_ignore_alerts.py`

**Note:** If more than one version of Python installed on the target machine, use the appropriate executables
for the installation and the execution (`pip3` and `python3` respectively)

### Configuration Parameters
```
===============================================================================================================
| Group         | Parameter            | Description                                                          |
===============================================================================================================
| DEFAULT       | wsUrl                | WhiteSource server URL. Can be found under the 'Integrate' tab in    |   
|               |                      | your WhiteSource organization.                                       |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | userKey              | WhiteSource User Key. Can be found under the 'Profile' section in    |
|               |                      | your WhiteSource organization.                                       |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | orgToken             | WhiteSource API Key. Can be found under the 'Integrate' tab in your  |
|               |                      | your WhiteSource organization.                                       |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | productToken         | WhiteSource Product Token. Can be found under the 'Integrate' tab    |  
|               |                      | in your WhiteSource organization.                                    |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | baselineProjectToken | Token of the WhiteSource project the ignored alerts are pulled from. |  
|               |                      | Can be found under the settings icon within a particular project.    |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProjectName      | Name of the WhiteSource project where the alerts will be ignored.    |  
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProjectVersion   | Version of the WhiteSource project where the alerts will be ignored. |  
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProjectToken     | Token of the WhiteSource project where the alerts will be ignored.   | 
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProductToken     | Token of the WhiteSource product where the alerts will be ignored.   | 
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | whitelist            | File with list of CVEs or list of CVEs divided by comma. *           | 
===============================================================================================================
```
'* The file should contain the list of CVEs like this:  
CVE-xxxx-yyyy  
CVE-zzzz-mmmm  
CVE-uuuu-nnnn

## Failing a build after running the utility
You can utilize the Mend API to fail a build after running the ws-ignore-alerts utility. The following API will provide all of the policy violations for the new project: [Get Project Security Alerts](https://docs.mend.io/bundle/mend-api-2-0/page/index.html#tag/Alerts-Project/operation/getSecurityVulnerabilityAlerts)

### Example Execution
- `export login=$(curl -X POST https://api-<mendURL>/api/v2.0/login -H "Content-Type: application/json" -d "{ \"email\": \"<ServiceUserEmail>\", \"orgToken\": \"<OrgToken>\", \"userKey\": \"<ServiceUserKey\" }")`
- `curl -s -H "Authorization: Bearer  $(jq -r  '.retVal.jwtToken' <<< "${login}")" 'https://api-<mendURL>/api/v2.0/<DestProjectToken>/alerts/legal?pageSize=50&page=0&search=type:equals:POLICY_VIOLATIONS' | jq -r .additionalData.totalItems`

If additionalItems returns a value > 0 you can exit the build

### Author
WhiteSource Software ©
