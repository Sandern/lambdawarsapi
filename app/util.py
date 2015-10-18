from valve.steam.id import SteamID
import bitstruct
import requests

from . import app

auth_url = app.config['STEAM_API_BACKEND_URL'] + 'ISteamUserAuth/AuthenticateUserTicket/v0001'


def build_steamid(steamid_unparsed):
    if steamid_unparsed.isdigit():
        universe, type, instance, account_number = bitstruct.unpack('u8u4u20u32',
                             bitstruct.pack('u64', int(steamid_unparsed)))

        if instance == 1:
            instance = 0
            account_number = int(account_number / 2)

        return SteamID(account_number, instance, type, universe)


    id = SteamID.from_text(steamid_unparsed)
    return id


def authenticate_ticket(ticket):
    """  Checks if session ticket is valid.

        A good response looks something like:
        {
            response: {
                params: {
                    result: "OK",
                    steamid: "76561197967932376",
                    ownersteamid: "76561197967932376"
                }
            }
        }
    """
    r = requests.get(auth_url, params={
        'key': app.config['PUBLISHER_WEBAPI_KEY'],
        'appid': 270370,
        'ticket': ticket,
    })

    resp = r.json()

    print('Steam api response: ', resp)

    params = resp['response']['params']

    if params['result'] != 'OK':
        return None

    return build_steamid(params['steamid'])
