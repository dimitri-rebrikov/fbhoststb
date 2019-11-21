import fritzconnection as fc
import json
import telegram
import os
from time import localtime, strftime
import sys

# function to detect the network 
# based on netnwork address prefixes 
def detectNetworkName(networkMapping, ip):
    for network in networkMapping.keys():
        if ip.startswith(network):
            return networkMapping[network]
    # don't found any matching name: use just the ip
    return ip

# default path to the config file
configFilePath='./fbhoststb.cfg'
# the path to the config file might be provided as 1st parameter
if len(sys.argv) > 1:
    configFilePath=sys.argv[1]
# load config
configFile = open(configFilePath, 'r')
config = json.load(configFile)
configFile.close()

storage={}
# load stored hosts
if os.path.isfile(config['storage']):
    f = open(config['storage'], 'r')
    storage=json.load(f)
    f.close()

# load current hosts from FritzBox
fh = fc.FritzHosts(**config['fritzbox'])
hosts = fh.get_hosts_info()

# compare stored with current and update
changed=False
for index, host in enumerate(hosts):
    mac = host.get('mac')
    ip = host.get('ip')
    name = host.get('name')
    # decode the connection status
    status = 'connected' if host.get('status') == '1' else 'disconnected'
    # get the stored host info 
    storedHost = storage.get(mac)
    if storedHost == None or storedHost.get('ip') != ip or storedHost.get('status') != status:
        # if there is no stored host or the ip or status has changed 
        # create the new host entry
        newHost = {
            'ip': ip, 
            'name': name,
            'network': detectNetworkName(config['networkMapping'],ip),
            'status': status, 
            'time': strftime("%Y-%m-%d %H:%M:%S", localtime()),
        }
        # store the new host entry (overwriting the old one if there)
        storage[mac] = newHost
        # set the flag that the data has changed
        changed = True
        # sent the message over Telegram Bot
        bot = telegram.Bot(token = config['telegram']['token'])
        bot.send_message(chat_id = config['telegram']['chatId'],
            text='{status} {name} on {network}'.format(**newHost) 
        )

if changed:
    # if there are changes
    # sore the data 
    f = open(config['storage'], 'w')
    json.dump(storage, f, sort_keys=True, indent=4)
    f.close()