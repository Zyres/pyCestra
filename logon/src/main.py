import sys
import time

import dataSource
from core.console import Console
from core.logging_handler import Logging, bcolors
from core.server_config import Config
from exchange.exchange_server import ExchangeServer
from login.login_server import LoginServer


def main():
    #  ======================================================
    #  start message

    log = Logging()
    console = Console()
    console.clear()

    def wel():
        welmsg = [58*'─', '|  0.01  |' + 12*' ' + 
                'pyCestra - Logon Server'+ 12*' ' + '|', 58*"─"]
        for x in welmsg:
            print(bcolors.blue + x + bcolors.cend)
    wel()

    # ======================================================
    # preload data

    config = Config()
    config.initialize()

    log.info('Connection Test...')
    database = dataSource.Database()
    if database.get_connection():
        log.info('Connection Successfully')
    else:
        log.warning('Connection ERROR')
        sys.exit(0)

    hostList = dataSource.ServerData()
    hostList.load()
    hostList = hostList.get_server_data()
    log.info('ServerData were loaded')

    accountData = dataSource.AccountData()
    accountData.load()
    accountDataDic = accountData.get_account_data()
    log.info('AccountData were loaded')

    ipbans = dataSource.IpBans().load()
    log.info('IP Bans were loaded')

    dataSource.DatabaseUpdateService().start(accountDataDic,
                                            config.get_update_time())

    # ======================================================
    # socket tests

    print(58*'-')

    game_client_dic = {}

    LoginServer().start(config.get_login_ip(),
                        config.get_login_port(),
                        game_client_dic,
                        accountDataDic,
                        hostList,
                        ipbans)

    ExchangeServer().start(config.get_exchange_ip(),
                        config.get_exchange_port(),
                        hostList)

    while True:
        time.sleep(15)
        log.warning('---- game_client_dic ----')
        for x in game_client_dic:
            log.warning(str(x))
        log.warning('-------------------------')

    # ======================================================

if __name__ == '__main__':
    main()
