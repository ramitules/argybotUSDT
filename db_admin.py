import sqlite3 as sql
from pprint import pprint

con = sql.connect('argybotUSDT.db')

while True:
    print('\nSeleccionar opcion')
    print('1. Listar todo')
    print('2. Listar ultimos 5')
    print('3. Agregar fila')
    
    print('0. Salir')
    opc = input('Opcion: ')

    if opc == '0':
        break

    if opc == '1':
        lista = con.execute('SELECT * FROM info_precios').fetchall()
        pprint(lista)

    if opc == '2':
        lista = con.execute('SELECT * FROM info_precios').fetchall()[-5:]
        pprint(lista)

    if opc == '3':
        query = 'INSERT INTO info_precios (fecha, hora, compra, venta, promedio) VALUES (?, ?, ?, ?, ?)'
        fecha = input('Fecha: ')
        hora = input('Hora: ')
        compra = input('Compra: ')
        venta = input('Venta: ')
        promedio = (float(compra) + float(venta)) / 2
        data = (fecha, int(hora), float(compra), float(venta), promedio)
        con.execute(query, data)
        con.commit()
        print(data)
        print('Ejecutado con exito')

    opc2 = input('Continuar? s/n: ')

    if opc2 == 'n':
        break

con.close()
