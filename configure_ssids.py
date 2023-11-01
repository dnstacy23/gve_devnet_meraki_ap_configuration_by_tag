#!/usr/bin/env python3
"""
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
import sys, os
import meraki
import json
from dotenv import load_dotenv
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress

def get_network_id(dashboard, org_id, net_name):
    """
    Connect to the Meraki dashboard and retrieve the networks of the org
    Then find the network id corresponding to the network name provided
    in the environmental variables
    :return: string containing the network id or None if no id found
    """
    networks = dashboard.organizations.getOrganizationNetworks(org_id,
                                                              total_pages="all")
    for network in networks:
        if network["name"] == net_name:
            return network["id"]

    return None

def get_wireless_networks(dashboard, org_id):
    """
    Connect to the Meraki dashboard and retrieve all the wireless networks in
    the org
    :return: list containing the details of each of the wireless networks
    """
    networks = dashboard.organizations.getOrganizationNetworks(org_id,
                                                               total_pages="all")
    wireless_networks = []
    for network in networks:
        if "wireless" in network["productTypes"]:
            wireless_networks.append(network)

    return wireless_networks

def get_all_ssids(dashboard, wireless_networks):
    """
    Iterate through the list of wireless networks and retrieve all the SSIDs
    for each network. Add the SSIDs to a list if it is not an Unconfigured SSID
    :return: list containing the details of the configured SSIDs
    """
    total_nets = len(wireless_networks)
    with Progress() as progress:
        overall_progress = progress.add_task("Overall Progress",
                                             total=total_nets, transient=True)
        all_ssids = []
        for net in wireless_networks:
            progress.console.print(f"Retrieving SSIDs for the {net['name']} network")
            ssids = dashboard.wireless.getNetworkWirelessSsids(net["id"])
            for ssid in ssids:
                if not ssid["name"].startswith("Unconfigured"):
                    all_ssids.append(ssid)

            progress.update(overall_progress, advance=1)

    return all_ssids

def make_ssid_dict(ssids):
    """
    Iterate through the SSIDs and create a dictionary that maps the SSID name
    to the details of the SSID
    :return: dictionary with keys that are the names of the SSIDs and the SSID details as the values
    """
    ssid_dict = {}
    for ssid in ssids:
        name = ssid["name"]
        ssid_dict[name] = ssid

    return ssid_dict

def get_ap_ssids(dashboard, org_id, net_id, ssids):
    """
    Get all the AP tags in the network that correspond to existing SSID names
    :return: set of the AP tag names that correspond to existing SSID names
    """
    total_ssids = len(ssids)
    network_ssids = set()
    with Progress() as progress:
        overall_progress = progress.add_task("Overall Progress",
                                             total=total_ssids, transient=True)
        for ssid in ssids:
            tag = ssid["name"]
            progress.console.print(f"Retrieving all APs with the tag {tag}")
            aps = dashboard.organizations.getOrganizationDevices(org_id,
                                                                 total_pages="all",
                                                                 networkIds=[net_id],
                                                                 tags=[tag],
                                                                 tagsFilterType="withAnyTags",
                                                                 productTypes=["wireless"])
            for ap in aps:
                network_ssids.add(tag)

            progress.update(overall_progress, advance=1)

    return network_ssids

def configure_net_ssids(dashboard, net_id, ssid_config):
    """
    Configure an SSID in the network
    :return: Boolean value indicating whether the SSID was successfully configured
    """
    ssid_config["number"] = 3 #the SSID configured will always be the 4th SSID (0-based index)
    ssid_num = ssid_config.pop("number")
    try:
        response = dashboard.wireless.updateNetworkWirelessSsid(net_id, ssid_num,
                                                                **ssid_config)
        return True
    except Exception as e:
        print(f"There was an issue configuring the SSID {ssid_config['name']} for the following reason:")
        print(e)

        return False

def get_psk_net_ssids(dashboard, net_id):
    """
    Connect to the Meraki dashboard and retrieve all the SSIDs that have a PSK
    configured as the auth mode
    :return: list containing the name and number of the PSK SSIDs
    """
    psk_ssids = []
    ssids = dashboard.wireless.getNetworkWirelessSsids(net_id)
    for ssid in ssids:
        if ssid["authMode"] == "psk":
            psk_ssid = {
                "name": ssid["name"],
                "number": ssid["number"],
                "net_id": net_id
            }
            psk_ssids.append(psk_ssid)

    return psk_ssids

def change_ssid_psk(dashboard, net_id, ssid_num, psk):
    """
    Configure a new PSK on the SSID in the network
    :return: Boolean value indicating whether the PSK was successfully updated
    """
    try:
        response = dashboard.wireless.updateNetworkWirelessSsid(net_id, ssid_num,
                                                                authMode="psk",
                                                                psk=psk)
        return True
    except Exception as e:
        print(f"There was an issue assigning a new password to the SSID for the following reason:")
        print(e)

        return False

def main(argv):
    # retrieve the environmental variables
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    NET_NAMES = json.loads(os.getenv("NETWORK_NAMES"))
    ORG_ID = os.getenv("ORG_ID")

    console = Console()
    console.print(Panel.fit(f"Meraki AP SSID Configuration"))

    # connect to the Meraki dashboard
    console.print(Panel.fit(f"Connect to Meraki dashboard", title="Step 1"))
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    # find the network id corresponding to the network name given in the environmental variables
    net_id_to_name = {}
    for network in NET_NAMES:
        console.print(Panel.fit(f"Get network ID for network {network}", title="Step 2"))
        net_id = get_network_id(dashboard, ORG_ID, network)
        if net_id is None:
            print(f"There was an error trying to find the network with name {network}")
            print("Aborting program...")

            return

        net_id_to_name[net_id] = network


    # retrieve all the wireless networks in the Meraki organization
    console.print(Panel.fit(f"Get all wireless networks from the Meraki organization",
                            title="Step 3"))
    wireless_networks = get_wireless_networks(dashboard, ORG_ID)

    # retrieve all the configured SSIDs from  the Meraki organization
    console.print(Panel.fit(f"Retrieve all the SSIDs from the Meraki organization",
                            title="Step 4"))
    all_ssids = get_all_ssids(dashboard, wireless_networks)
    ssid_dict = make_ssid_dict(all_ssids)

    # retrieve all the SSID names that correspond to the AP tags
    console.print(Panel.fit(f"Find which SSIDs need to be configured by AP tags",
                            title="Step 5"))
    network_to_ssids = {}
    for net_id in net_id_to_name:
        network_to_ssids[net_id] = get_ap_ssids(dashboard, ORG_ID, net_id, all_ssids)

    # configure the SSIDs that match AP tags in the network
    console.print(Panel.fit(f"Configure networks with the necessary SSIDs",
                            title="Step 6"))
    total_ssids = 0
    for network in network_to_ssids:
        total_ssids += len(network_to_ssids[network])

    with Progress() as progress:
        overall_progress = progress.add_task("Overall Progress", total=total_ssids,
                                             transient=True)
        for net_id in network_to_ssids:
            progress.console.print(f"Configuring the SSIDs of the {net_id_to_name[net_id]} network")
            for ssid_name in network_to_ssids[net_id]:
                ssid = ssid_dict[ssid_name]
                configured = configure_net_ssids(dashboard, net_id, ssid)
                if configured:
                    print(f"{net_id_to_name[net_id]} configured with ssid {ssid_name}")
                else:
                    print(f"There was an issue configuring ssid {ssid_name} on {net_id_to_name[net_id]}")

                progress.update(overall_progress, advance=1)

    # provide the user an option to change the PSK on the SSIDs in the network with PSKs
    console.print(Panel.fit(f"Configure new passwords on SSIDs", title="Step 7"))
    psk_ssids = []
    for net_id in network_to_ssids:
        psk_ssids += get_psk_net_ssids(dashboard, net_id)

    for ssid in psk_ssids:
        index = psk_ssids.index(ssid)
        net_name = net_id_to_name[ssid["net_id"]]
        print(f"{index} - {ssid['name']} of {net_name}")

    # continue asking the user if they would like to change the PSK until they say otherwise
    ssid_index = input("Enter the number corresponding to the SSID whose password you'd like to change or enter N for none: ")
    while ssid_index.lower() != "n":
        ssid_index = int(ssid_index)
        ssid_num = psk_ssids[ssid_index]["number"]
        ssid_name = psk_ssids[ssid_index]["name"]
        net_id = psk_ssids[ssid_index]["net_id"]
        net_name = net_id_to_name[net_id]
        new_psk = input("Enter the new password you'd like to assign to the SSID: ")
        configured = change_ssid_psk(dashboard, net_id, ssid_num, new_psk)
        if configured:
            print(f"{ssid_name} of network {net_name} configured with a new psk")
        else:
            print(f"There was an issue configuring a new psk for {ssid_name} of network {net_name}")

        ssid_index = input("Enter the number corresponding to the SSID whose password you'd like to change or enter N for none: ")



if __name__ == "__main__":
    sys.exit(main(sys.argv))
