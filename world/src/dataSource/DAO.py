import dataSource
import mysql.connector
from core.logging_handler import Logging


class DAO:

    def __init__(self):
        self.log = Logging()
        self.connection = dataSource.Database().get_connection()
        self.cursor = self.connection.cursor()

    def get_data(self, query):
        connection = dataSource.Database().get_connection()
        cursor = connection.cursor()
        try:
            if not query.endswith(';'):
                    query += ";"
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except Exception as e:
            self.log.warning('DAO.py - Can\'t load: \n{}\n{}'.format(query,str(e)))
            cursor.close()
            connection.close()
        finally:
            cursor.close()
            connection.close()

    def multi_update_data(self, query):
        '''
        This function does not end the connection after use
        '''
        try:
            if not query.endswith(';'):
                    query += ";"
            self.cursor.execute(query)
        except pymysql.Error as Error:
            self.log.warning('DAO.py - update_data - Can\'t update the Database\n{}\n{}'.format(str(Error),query))
