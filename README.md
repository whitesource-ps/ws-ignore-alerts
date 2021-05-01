![Logo](https://whitesource-resources.s3.amazonaws.com/ws-sig-images/Whitesource_Logo_178x44.png)  

[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub release](https://img.shields.io/github/v/release/whitesource-ps/ws-ignore-alerts)](https://github.com/whitesource-ps/ws-ignore-alerts/releases/latest) 
[![WS Ignore Alerts Build and Publish](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml/badge.svg)](https://github.com/whitesource-ps/ws-ignore-alerts/actions/workflows/ci.yml)
[![Python 3.6](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Blue_Python_3.6%2B_Shield_Badge.svg/86px-Blue_Python_3.6%2B_Shield_Badge.svg.png)](https://www.python.org/downloads/release/python-360/)
```
 _          ___     _ _        _____
\ \        / / |   (_) |      / ____|                        
 \ \  /\  / /| |__  _| |_ ___| (___   ___  _   _ _ __ ___ ___
  \ \/  \/ / | '_ \| | __/ _ \\___ \ / _ \| | | | '__/ __/ _ \
   \  /\  /  | | | | | ||  __/____) | (_) | |_| | | | (_|  __/
    \/  \/   |_| |_|_|\__\___|_____/ \___/ \__,_|_|  \___\___
```

# Ignore Future Alerts 
**ws_ignore_alerts.py** is a utility for ignoring alerts in the new project, accordingly to the already ignored alerts 
in the previous project, which is a version of the same WS product.  
As an example, there is a WS product where each WS project is a version. After each WS scan a new project will be created and 
once it is done the utility can be launched as part of the pipeline. All ignored alerts will be pulled from the last updated 
project, and the same alerts will be ignored in the new project.

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
- `python ws_ignore_alerts.py -u $wsUrl -k $userKey -o $orgToken -p $productToken`

Using a config file:
- `python ws_ignore_alerts.py`

**Note:** If more than one version of Python is installed on the target machine, use the appropriate executables
for the installation and the execution (`pip3` and `python3` respectively)

### Configuration Parameters
```
=========================================================================================================
| Group         | Parameter      | Description                                                          |
=========================================================================================================
| DEFAULT       | WsUrl          | WhiteSource server URL. Can be found under the 'Integrate' tab in    |   
|               |                | your WhiteSource organization                                        |
---------------------------------------------------------------------------------------------------------
| DEFAULT       | UserKey        | WhiteSource User Key. Can be found under the 'Profile' section in    |
|               |                | your WhiteSource organization.                                       |
---------------------------------------------------------------------------------------------------------
| DEFAULT       | OrgToken       | WhiteSource API Key. Can be found under the 'Integrate' tab in your  |
|               |                | your WhiteSource organization.                                       |
---------------------------------------------------------------------------------------------------------
| DEFAULT       | ProductToken   | WhiteSource Product Token. Can be found under the 'Integrate' tab    |  
|               |                | in your WhiteSource organization.                                    |
=========================================================================================================
```

### Author
WhiteSource Software ©
