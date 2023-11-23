import sqlite3 as sql


class DBHandler:
    def __init__(self):
        self.connection = sql.connect('argybotUSDT.db')
        self._check_tables()

    def _check_tables(self):
        cursor = self.connection.cursor()

        try:
            cursor.execute('SELECT * FROM keys')

        except sql.OperationalError:
            self.create_table_k()

        try:
            cursor.execute('SELECT * FROM info_precios')

        except sql.OperationalError:
            self.create_table_p()

        cursor.close()

    def create_table_k(self):
        query = '''CREATE TABLE keys (
                consumer_key TEXT NOT NULL,
                consumer_secret TEXT NOT NULL)'''

        with self.connection:
            self.connection.execute(query)

        consumer_k = input('Input here your consumer key from Twitter API: ')
        consumer_s = input('Input here your consumer secret from Twitter API: ')

        query = 'INSERT INTO keys (consumer_key, consumer_secret) VALUES (?, ?)'

        with self.connection:
            self.connection.execute(query, (consumer_k, consumer_s))

    def create_table_p(self):
        query = '''CREATE TABLE info_precios (
                fecha TEXT DEFAULT CURRENT_DATE,
                hora INTEGER NOT NULL,
                compra REAL NOT NULL,
                venta REAL NOT NULL,
                promedio REAL NOT NULL)'''

        with self.connection:
            self.connection.execute(query)

    def get_keys(self):
        try:
            with self.connection:
                res = self.connection.execute('SELECT * FROM keys')

        except sql.Error as err:
            print(f'Unexpected error: {err}')
            exit(1)

        keys = res.fetchall()[0]

        d_keys: dict[str, str] = {
            'consumer_key': keys[0],
            'consumer_secret': keys[1]
        }

        return d_keys

    def add_row(self, hora: int, compra: float, venta: float, promedio: float):
        query = 'INSERT INTO info_precios (hora, compra, venta, promedio) VALUES (?, ?, ?, ?)'

        data = (hora, compra, venta, promedio)

        try:
            with self.connection:
                self.connection.execute(query, data)

        except sql.Error as err:
            print(f'Unexpected error: {err}')

    def get_row(self, hora: int, fecha: str):
        query = 'SELECT * FROM info_precios WHERE fecha = ? AND hora = ?'

        with self.connection:
            res = self.connection.execute(query, (fecha, hora))

        res = res.fetchone()

        return {
            'fecha': res[0],
            'hora': res[1],
            'compra': res[2],
            'venta': res[3],
            'promedio': res[4]
        }
