import sqlite3


class Model:
    def __init__(self, db, table):
        self.db = db
        self.table = table
        self.connection = sqlite3.connect(db + '.db')
        self.connection.row_factory = sqlite3.Row

    def create(self, row):
        bindings = '('
        keys = '('
        values = []
        i = 0
        for key, value in row.items():
            bindings += '?'
            keys += key
            values.append(value)
            i += 1
            if i != (len(row)):
                bindings += ', '
                keys += ', '
        bindings += ')'
        keys += ')'
        sql = 'INSERT INTO {} {} VALUES {}'.format(self.table, keys, bindings)
        print(sql, values)
        self.connection.execute(sql, values)
        self.connection.commit()

    def read(self):
        sql = 'SELECT * FROM {}'.format(self.table)
        print(sql)
        cursor = self.connection.execute(sql)
        rows = []
        for row in cursor:
            print(dict(row))
            rows.append(row)
        return rows

    def update(self, row, where):
        keys = ''
        values = []
        i = 0
        for key, value in row.items():
            keys += key + ' = ?'
            values.append(value)
            i += 1
            if i != len(row):
                keys += ', '
        sql = 'UPDATE {} SET {} WHERE {} = {}'.format(self.table, keys, where['key'], where['value'])
        print(sql, values)
        self.connection.execute(sql, values)
        self.connection.commit()

    def delete(self, where):
        sql = 'DELETE FROM {} WHERE {} = {}'.format(self.table, where['key'], where['value'])
        print(sql)
        self.connection.execute(sql)
        self.connection.commit()
