from enum import Enum

from core.logging_handler import Logging
from dataSource.account_data import AccountData
from login.packet.account_queue import AccountQueue
from login.packet.choose_nickname import ChooseNickName
from login.packet.server_list import ServerList
from object.account import Account


class PacketHandler:

    def __init__(self):
        self.log = Logging()

    def parser(self, client, packet, game_client_dic, accountDataDic, hostList):
        # client arrived here, the version has been checked
        if client.get_status().name == Status.WAIT_VERSION.name:
            # set client status to WAIT_ACCOUNT
            client.set_status(Status(2))
            self.log.debug('[' + str(client.get_address()[0]) + ':' +
                            str(client.get_address()[1]) + ']' +
                            '[' + str(client.get_status().name) + '] Status change')

        if  client.get_status().name == Status.WAIT_ACCOUNT.name:
            verifyAccountName = PacketHandler().verify_account_name(client, packet.split('\n')[0], accountDataDic)
            verifyPassword = PacketHandler().verify_password(client, packet.split('\n')[1])
            if not (verifyAccountName and verifyPassword):
                self.log.debug('[' + str(client.get_address()[0]) + ':' +
                            str(client.get_address()[1]) + ']' +
                            '[' + str(client.get_status().name) + '] Login credentials incorrect')
                client.write('AlEf')

        if  client.get_status().name == Status.WAIT_NICKNAME.name:
            ChooseNickName().verify(client, packet[:-2], accountDataDic, hostList)
            return

        if  client.get_status().name == Status.SERVER.name:
            if (packet[0:2] == 'AF') or (packet[-4:-2] == 'AF'):
                # FriendServerList.get(client, packet)
                print('packet[0:2] == AF:')
            elif (packet[0:2] == 'AX') or (packet[-4:-2] == 'AX'):
                # ServerSelected.get()
                print('packet[0:2] == AX:')
            elif (packet[0:2] == 'Af') or (packet[-4:-2] == 'Af'):
                account = client.get_account()
                for game_client in game_client_dic.values():
                    if not game_client.get_key() == client.get_key():
                        dic_account = game_client.get_account()
                        if dic_account.get_id() == account.get_id():
                            self.log.debug('[' + str(client.get_address()[0]) + ':' +
                                            str(client.get_address()[1]) + ']' +
                                            '[' + str(client.get_status().name) + '] ' +
                                            'this account is already logged in ...' +
                                            'the other session is now closed')
                            game_client.kick()
                AccountQueue().verify(client, accountDataDic, hostList)
                return

            elif (packet[0:2] == 'Ax') or (packet[-4:-2] == 'Ax'):
                ServerList().get_list(client)
                return

            client.kick()
        client.kick()

    def verify_account_name(self, client, name, accountDataDic):
        # accountDataDic is checked whether the account exists
        def load_from_result_set(resultSet):
            account = Account()
            account.set_id(resultSet['id'])
            account.set_name(resultSet['account'])
            account.set_pass(resultSet['pass'])
            account.set_nickname(resultSet['nickname'])
            account.set_question(resultSet['question'])
            account.set_state(resultSet['logged'])
            account.set_subscribe(resultSet['subscribe'])
            account.set_banned(resultSet['banned'])
            account.set_staff(resultSet['rank'])
            return account

        for i in accountDataDic:
            if i['account'] == name:
                account = load_from_result_set(i)
                client.set_account(account)
                break
            else:
                account = 0

        if account == 0:
            return False
        client.get_account().set_client(client)
        # set client status to WAIT_PASSWORD
        client.set_status(Status(1))
        self.log.debug('[' + str(client.get_address()[0]) + ':' +
                        str(client.get_address()[1]) + ']' +
                        '[' + str(client.get_status().name) + '] Status change')
        return True

    def verify_password(self, client, password):
        account = client.get_account()
        if account == 0:
            return False
        if not PacketHandler().decrypt_password(password[2:], client.get_key()) == account.get_pass():
            return False
        # set client status to SERVER
        client.set_status(Status(4))
        self.log.debug('[' + str(client.get_address()[0]) + ':' +
                        str(client.get_address()[1]) + ']' +
                        '[' + str(client.get_status().name) + '] Status change')
        return True

    def decrypt_password(self, passs, key):
        _Chaine = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
        _decrypted = ""
        for i in range(len(passs)//2):
            _PKey = ord(key[i])
            _ANB = _Chaine.index(passs[i*2])
            _ANB2 = _Chaine.index(passs[i*2+1])
            _somme1 = _ANB + len(_Chaine)
            _somme2 = _ANB2 + len(_Chaine)
            _APass = _somme1 - _PKey
            if _APass < 0:
                _APass += 64
            _APass *= 16
            _AKey = _somme2 - _PKey
            if _AKey < 0:
                _AKey += 64
            _PPass = chr(_APass + _AKey)
            _decrypted = _decrypted + _PPass
        return _decrypted

class Status(Enum):
    WAIT_VERSION = 0
    WAIT_PASSWORD = 1
    WAIT_ACCOUNT = 2
    WAIT_NICKNAME = 3
    SERVER = 4
