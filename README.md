# GVE DevNet Meraki AP SSID Configuration by Tag
This repository contains the source code of a Python script that can configure the SSIDs of Meraki wireless networks according to the tags of the APs in those networks. The script matches the AP's tag with the name of an SSID configured elsewhere in the Meraki org. Then the script copies that SSID's configuration into the network of the AP, so that the AP is also broadcasting that SSID in its own network. The script will also offer the option to change the PSK of the SSIDs in the networks.

## Contacts
* Danielle Stacy

## Solution Components
* Python 3.11
* Meraki SDK

## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`
3. Click on `Enable access to the Cisco Meraki Dashboard API`
4. Go to `My Profile > API access`
5. Under API access, click on `Generate API key`
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

> Note: You can add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).

#### Organization ID and Network Name
Before running the code, you must know which Meraki organization and which network(s) in that organization you will be configuring. You will need to record the name of the network(s) and the organization ID in the Installation/Configuration section.
To find the organization ID, follow these steps:
1. Login to the Meraki dashboard
2. In the left-hand menu, select the dropdown menu of organizations. Then choose the name of the organization which you will be configuring
3. Once you are brought to the Organization Summary page, scroll to the bottom of the page. Here, you should find login and session information. At the very bottom of the page, it will list the hosting information of your Meraki organization, which should include your organization ID
4. Copy and save the organization ID in a safe place

## Installation/Configuration
1. Clone this repository with `git clone [repository name]`. To find the repository name, click the green Code button above the repository files. Then, the dropdown menu will show the https domain name. Click the copy button to the right of the domain name to get the value to replace [repository name] placeholder.
2. Add Meraki API key, organization ID, and network name(s) to environment variables. If you are only configuring one network, just place one network name in double quotations in between the square brackets. Do not include commas
```python
API_KEY = "API key goes here"
ORG_ID = "org id goes here"
NETWORK_NAME = ["network names goes here", "separated by commas in double quotes"]
```
3. Set up a Python virtual environment. Make sure Python 3 is installed in your environment, and if not, you may download Python [here](https://www.python.org/downloads/). Once Python 3 is installed in your environment, you can activate the virtual environment with the instructions found [here](https://docs.python.org/3/tutorial/venv.html).
4. Install the requirements with `pip3 install -r requirements.txt`

## Usage
To run the program, use the command:
```
$ python3 configure_ssids.py
```

As the program runs, it will print out information about the API calls it makes and their success.

![/IMAGES/screenshot1.png](/IMAGES/screenshot1.png)

![/IMAGES/screenshot2.png](/IMAGES/screenshot2.png)

![/IMAGES/screenshot3.png](/IMAGES/screenshot3.png)

After the SSIDs are copied over, the code will prompt the user if they wish to change any of the PSKs in the network.

![/IMAGES/screenshot4.png](/IMAGES/screenshot4.png)

Once you type N, the code exits.

> Note: The SSID configured in the network will always be the fourth SSID in the network. To change this, change the code on line 121. Simply set the ssid_config["number"] variable equal to the index of the SSID number in the dashboard, so 0 is the first, 1 is the second, 2 is thid, and so on.
```python
ssid_config["number"] = 3 #the SSID configured will always be the 4th SSID (0-based index)
```

![/IMAGES/0image.png](/IMAGES/0image.png)


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
