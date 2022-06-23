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
- using a baseline project token and destination project name defined by the user - baselineProjectToken and destProjectName (optional: destProjectVersion). Might be different products.
- using a baseline project token and destination project token defined by the user - baselineProjectToken and destProjectToken. Might be different products
- using the default behavior, without providing baseline and destination projects' data. In this case, the destination project is a recent project of the certain product 
  and baseline project is one before the recent project of the same product. Only works within a certain product.
The ignored alerts will be pulled from the baseline project, and the same alerts will be ignored in the destination project.

### Supported Operating Systems
- Linux (Bash): CentOS, Debian, Ubuntu, RedHat
- Windows (PowerShell): 10, 2012, 2016

### Prerequisites
- Python 3.5 or above

 

### Execution
From the command line:
- `python ws_ignore_alerts.py -u $wsUrl -k $userKey -o $orgToken -p $productToken -b $baselineProjectToken -n 
  $destProjectName -v $destProjectVersion -t $destProjectToken`

Using a config file:
- `python ws_ignore_alerts.py`

**Note:** If more than one version of Python is installed on the target machine, use the appropriate executables
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
| DEFAULT       | destProjectTokne     | Token of the WhiteSource project where the alerts will be ignored.   | 
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProductTokne     | Token of the WhiteSource product where the alerts will be ignored.   | 
===============================================================================================================
```

### Author
WhiteSource Software ©
