import fritzconnection as fc
import json
import telegram
import os
from time import localtime, strftime, sleep
import sys

# function to provide formatted time
def getFormattedTime():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())

# function to detect the network 
# based on netnwork address prefixes 
def detectNetworkName(networkMapping, ip):
    if ip != None:
        for network in networkMapping.keys():
            if ip.startswith(network):
                return networkMapping[network]
    # don't found any matching name: use just the ip
    return ip

# history file name
def getHistoryFileName():
    return '{}.dat'.format(strftime("%Y-%m-%d", localtime()))

# default path to the config file
configFilePath='./fbhoststb.cfg'
# the path to the config file might be provided as 1st parameter
if len(sys.argv) > 1:
    configFilePath=sys.argv[1]
# load config
with open(configFilePath, 'r') as configFile:
    config = json.load(configFile)

# create history dir
os.makedirs(config['historyDir'], exist_ok=True)

storage={}
# load stored hosts
if os.path.isfile(config['storage']):
    with open(config['storage'], 'r') as f:
        storage=json.load(f)

# initalize Fritz Box connection
fh = fc.FritzHosts(**config['fritzbox'])
# initialize Telegram connection
bot = telegram.Bot(token = config['telegram']['token'])

while True: # infinite loop
    # load current hosts from FritzBox
    try:
        hosts = fh.get_hosts_info()
    except KeyError:
        # the KeyError happens sporadically 
        print('{}: got KeyError from FritzBox get_hosts_info()'.format(getFormattedTime()))
        # prevent high frequent polling if the error happens permanently
        sleep(5)
        # retry
        continue
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
                'time': getFormattedTime(),
            }
            # store the new host entry (overwriting the old one if there)
            storage[mac] = newHost
            # set the flag that the data has changed
            changed = True
            # prepare the message send it to stdout
            msg = '{name} {status} @ {network}'.format(**newHost)
            print('{}: {}'.format(getFormattedTime(), msg))
            # sent the message over Telegram Bot
            bot.send_message(
                chat_id = config['telegram']['chatId'],
                text = msg
            )
            # write into history
            with open('{dir}/{file}'.format(
                    dir=config['historyDir'], 
                    file=getHistoryFileName()),'a') as f:
                historyEntry = {
                    'mac':mac,  
                    'message':msg
                }
                historyEntry.update(newHost)
                json.dump(historyEntry, f)
                f.write('\n')

    if changed:
        # if there are changes
        # store the data 
        with open(config['storage'], 'w') as f:
            json.dump(storage, f, sort_keys=True, indent=4)
 
    sleep(30)