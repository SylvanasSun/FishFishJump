import logging
import sqlite3

"""
The module for save persistent data that cannot be queried by scrapyd api. 
"""


class SqlLite3Agent(object):
    logging = logging.getLogger(__name__)
    SELECTION_TABLE_IS_EXISTED = 'SELECT count(*) FROM sqlite_master WHERE type=\'table\' AND name=\'%s\''
    SELECTION_ALL_TABLE_NAME = 'SELECT name FROM sqlite_master WHERE type=\'table\' ORDER BY name'
    SELECTION_ALL_TABLE = 'SELECT * FROM sqlite_master WHERE type=\'table\''

    def __init__(self, db_file_name):
        self.db_file_name = db_file_name

    def create_table(self, sql):
        table_name = sql[sql.find('TABLE') + 5:sql.find('(')].strip()
        is_existed = list(self.execute(__class__.SELECTION_TABLE_IS_EXISTED % table_name)[0])[0]
        if is_existed != 1:
            self.execute(sql)
            logging.debug('Creating table %s sql[%s] ' % (table_name, sql))
        else:
            logging.debug('Table %s is already exist so does not execute this sql' % table_name)

    def select_all_table_name(self):
        return [list(name)[0] for name in self.execute(__class__.SELECTION_ALL_TABLE_NAME)]

    def select_all_table_info(self):
        return [list(t) for t in self.execute(__class__.SELECTION_ALL_TABLE)]

    def execute(self, sql, *args):
        connection = None
        cursor = None
        try:
            connection = sqlite3.connect(self.db_file_name)
            cursor = connection.cursor()
            cursor.execute(sql, args)
            logging.debug('SQL completed [%s] ' % sql)
            return cursor.fetchall()
        finally:
            self.release(connection, cursor)

    def release(self, connection, cursor):
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.commit()
            connection.close()
