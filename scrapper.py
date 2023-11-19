import requests
import time
import datetime
from requests_oauthlib import OAuth1Session
import json
import pickle


def mainloop():
    range_hours = [hour for hour in range(9, 24)]  # Se ejecuta entre las 9 y las 23hs
    range_hours.append(int(0))  # Se agrega las 00hs
    h_now = datetime.datetime.now().hour  # Hora actual
    m_now = datetime.datetime.now().minute  # Minutos actuales

    p_anteriores = dict()
    with open('session.pkl', 'rb') as f:
        session = pickle.load(f)

    while True:
        #  if h_now in range_hours and m_now == 0:  # Si la hora actual esta dentro del rango operacional y minutos = 0
        p_actuales = fetch_data()
        data = twit_format(p_actuales, p_anteriores)
        post(session, data)
        p_anteriores = p_actuales

        h_now = datetime.datetime.now().hour
        m_now = datetime.datetime.now().minute
        print(f'{h_now}:{m_now}')

        time.sleep(60)  # Intervalo de actualizacion: cada un minuto


def connect():
    consumer_key = ''
    consumer_secret = ''

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


def calcular_varianza(dif: float):
    if dif > 0:
        varianza = 'subio {0:.2f}%'.format(dif)

    elif dif < 0:
        varianza = 'bajo {0:.2f}%'.format(dif)

    else:
        varianza = 'estable'

    return varianza


def fetch_data():
    req = requests.get('https://criptoya.com/api/binancep2p/usdt/ars')
    precios = req.json()

    p_compra = "{0:.2f}".format(precios['ask'])
    p_venta = "{0:.2f}".format(precios['bid'])

    datos = {
        "compra": p_compra,
        "venta": p_venta
    }

    return datos


def twit_format(p_nuevos: dict[str, str],
                p_viejos: dict[str, str] | None = None):
    if p_viejos:
        # COMPRA
        diferencia = float(p_viejos['compra']) / float(p_nuevos['compra']) - 1
        diferencia = diferencia * 100  # Diferencia en porcentaje

        varianza = calcular_varianza(diferencia)

        compra = f"Para la compra: ${p_nuevos['compra']} - {varianza}"

        # VENTA
        diferencia = float(p_viejos['venta']) / float(p_nuevos['venta']) - 1
        diferencia = diferencia * 100

        varianza = calcular_varianza(diferencia)

        venta = f"Para la venta: ${p_nuevos['venta']} - {varianza}"

    else:
        compra = f"Para la compra: ${p_nuevos['compra']}"
        venta = f"Para la venta: ${p_nuevos['venta']}"

    fuente = 'Fuente: [Binance P2P] https://criptoya.com/'

    data = '\n'.join([compra, venta, fuente])

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
