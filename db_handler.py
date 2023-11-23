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
                promedio REAL NOT NULL,
                CONSTRAINT id PRIMARY KEY(fecha, hora))'''

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

    def add_row(self, data):
        query = 'INSERT INTO info_precios (hora, compra, venta, promedio) VALUES (?, ?, ?, ?)'

        try:
            with self.connection:
                self.connection.execute(query, data)

        except sql.Error as err:
            print(f'Unexpected error: {err}')
