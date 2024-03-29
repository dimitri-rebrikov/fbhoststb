from fritzconnection.lib.fritzhosts import FritzHosts
import json
import telegram
import os
from time import localtime, strftime, sleep
import sys
import asyncio

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

async def main():
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
    fh = FritzHosts(**config['fritzbox'])
    # initialize Telegram connection
    bot = telegram.Bot(token = config['telegram']['token'])
    async with bot:
        await bot.send_message(
            chat_id = config['telegram']['chatId'],
            text = 'fbhoststb started'
        )

    while True: # infinite loop
        # load current hosts from FritzBox
        try:
            hosts = fh.get_hosts_info()
        except :
            # the errors happen sporadically 
            print('{}: got Exception from FritzBox get_hosts_info(): {}'
                .format(getFormattedTime(), sys.exc_info()[0]))
            # prevent high frequent polling if the error happens permanently
            sleep(10)
            # retry
            continue
        # compare stored with current and update
        changed=False
        for index, host in enumerate(hosts):
            # print(host)
            mac = host.get('mac')
            if not mac:
                # ignore devices without mac 
                continue
            ip = host.get('ip')
            name = host.get('name')
            # decode the connection status
            status = 'connected' if host.get('status') == True else 'disconnected'
            # get the stored host info 
            storedHost = storage.get(mac)
            if storedHost == None or storedHost.get('ip') != ip or storedHost.get('status') != status:
                # if there is no stored host or the ip or status has changed 
                #
                # get the interface (i.e. LAN/WiFI etc) from details           
                hostDetails = fh.get_specific_host_entry(host.get('mac'))
                interface = hostDetails.get('NewInterfaceType')
                # create the new host entry
                newHost = {
                    'ip': ip, 
                    'name': name,
                    'network': detectNetworkName(config['networkMapping'],ip),
                    'status': status, 
                    'time': getFormattedTime(),
                    'interface': config['interfaceMapping'].get(interface, interface)
                }
                # store the new host entry (overwriting the old one if there)
                storage[mac] = newHost
                # set the flag that the data has changed
                changed = True
                # prepare the message send it to stdout
                msg = '{name} {status} @ {network}({interface})'.format(**newHost)
                print('{}: {}'.format(getFormattedTime(), msg))
                # sent the message over Telegram Bot
                async with bot:
                    await bot.send_message(
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

asyncio.run(main())
