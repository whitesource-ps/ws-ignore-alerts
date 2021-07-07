![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-ignore-alerts)](https://github.com/whitesource-ps/ws-ignore-alerts/releases/latest) 
[![WS Ignore Alerts Build and Publish](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml)
[![Python 3.6](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Blue_Python_3.6%2B_Shield_Badge.svg/86px-Blue_Python_3.6%2B_Shield_Badge.svg.png)](https://www.python.org/downloads/release/python-360/)

# Ignore Future Alerts 
**ws_ignore_alerts.py** is a utility for ignoring alerts in the newly created WS Project, which is a version of the same customer's product, 
according to the already ignored alerts in the baseline WS Project. After each WS scan a new WS Project will be created and
once it is done the utility can be launched as part of the pipeline.
As an example, there are two options for use:
- using baseline project defined by the user - baselineProjectToken and destProjectName (destProjectVersion) are required parameters.
- using default baseline project which is the last updated project in the particular WS Product.
The alerts will be pulled from the baseline project, and the same alerts will be ignored in the new project.

### Supported Operating Systems
- Linux (Bash): CentOS, Debian, Ubuntu, RedHat
- Windows (PowerShell): 10, 2012, 2016

### Prerequisites
- Python 3.5 or above

### Deployment
1. Download and unzip **ws_ignore_alerts.zip**.
2. From the command line, navigate to the ws_ignore_alerts directory and install the package:  
   `pip install -r requirements.txt`
3. Edit the **params.config** file and update the relevant parameters (see the configuration parameters below) or 
   use a cmd line for running

### Execution
From the command line:
- `python ws_ignore_alerts.py -u $wsUrl -k $userKey -o $orgToken -p $productToken -b $baselineProjectToken -n 
  $destProjectName -v $destProjectVersion` 

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
| DEFAULT       | baselineProjectToken | WhiteSource Project Token that has already ignored alerts. Can be    |  
|               |                      | found under the 'Integrate' tab in your WhiteSource organization.    |
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProjectName      | The name of the new WhiteSource Project defined by the user.         |  
---------------------------------------------------------------------------------------------------------------
| DEFAULT       | destProjectVersion   | The version of the new WhiteSource Project defined by the user.      |  
===============================================================================================================
```

### Author
WhiteSource Software ©
