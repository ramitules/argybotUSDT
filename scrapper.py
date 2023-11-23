import requests
from requests_oauthlib import OAuth1Session
import json
import pickle
from datetime import datetime, timedelta
from db_handler import DBHandler


def main_func():
    db_handler = DBHandler()

    try:
        with open('session.pkl', 'rb') as f:
            session = pickle.load(f)

    except FileNotFoundError:
        session = connect(db_handler.get_keys())

    p_actuales = fetch_data()
    data = difference(p_actuales, db_handler)
    post(session, data)


def connect(keys: dict):
    consumer_key = keys['consumer_key']
    consumer_secret = keys['consumer_secret']

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    # Try to login
    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )
        return

    # Fetch tokens
    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print(f"Got OAuth token: {resource_owner_key}")

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print(f"Please go here and authorize: {authorization_url}")
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    return oauth


def varianza_str(dif: float):
    if dif > 0:
        varianza = 'subio {0:.2f}%'.format(dif)

    elif dif < 0:
        varianza = 'bajo {0:.2f}%'.format(dif)

    else:
        varianza = 'estable (0%)'

    return varianza


def fetch_data():
    req = requests.get('https://criptoya.com/api/binancep2p/usdt/ars')
    precios = req.json()

    p_compra = precios['ask']
    p_venta = precios['bid']

    datos = {
        "compra": p_compra,
        "venta": p_venta
    }

    return datos


def difference(p_nuevos: dict[str, float], db_handler: DBHandler):
    # Obtencion de datos de hace una hora
    hoy = datetime.now() - timedelta(hours=1)
    fecha = hoy.date().isoformat()
    hora = hoy.hour

    p_viejos = db_handler.get_row(hora, fecha)

    # COMPRA
    compra_str = '{0:.2f}'.format(p_nuevos['compra'])
    diferencia = (p_nuevos['compra'] / p_viejos['compra']) - 1
    diferencia *= 100  # Diferencia en porcentaje

    varianza = varianza_str(diferencia)

    compra = f"Para la compra: ${compra_str} - {varianza}"

    # VENTA
    venta_str = '{0:.2f}'.format(p_nuevos['venta'])
    diferencia = (p_nuevos['venta'] / p_viejos['venta']) - 1
    diferencia *= 100

    varianza = varianza_str(diferencia)

    venta = f"Para la venta: ${p_nuevos['venta']} - {varianza}"

    # Fuente a pagina web con API
    fuente = 'Fuente: [Binance P2P] https://criptoya.com/'

    # Promedios cada 24hs
    # Obtencion de datos de ayer
    ayer = datetime.now() - timedelta(days=1)
    fecha = ayer.date().isoformat()
    hora = ayer.hour

    p_viejos = db_handler.get_row(hora, fecha)

    prom = (p_nuevos['compra'] + p_nuevos['venta']) / 2  # Promedio

    diferencia = prom / p_viejos['promedio'] - 1
    diferencia *= 100

    varianza = varianza_str(diferencia)

    prom_24hs = f"Diferencia 24hs: {varianza}"

    # Unir datos y mostrarlos
    data = '\n'.join([compra, venta, prom_24hs, fuente])
    print('--Se tuiteara lo siguiente--')
    print(data, '\n-----------------------------')

    # Nueva fila a la base de datos
    db_handler.add_row(hora, p_nuevos['compra'], p_nuevos['venta'], prom)

    return data


def post(oauth: OAuth1Session, data: str):
    # El tuit
    tuit = {"text": data}

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=tuit
    )

    if response.status_code != 201:
        raise Exception(
            f"Request returned an error: {response.status_code} {response.text}"
        )

    print(f"Response code: {response.status_code}")

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))
