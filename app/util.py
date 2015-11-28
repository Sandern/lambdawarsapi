from valve.steam.id import SteamID
import bitstruct
import requests
from uuid import UUID

from . import app

auth_url = app.config['STEAM_API_BACKEND_URL'] + 'ISteamUserAuth/AuthenticateUserTicket/v0001'


def build_steamid(steamid_unparsed):
    if str(steamid_unparsed).isdigit():
        universe, steam_type, instance, account_number = bitstruct.unpack('u8u4u20u32',
                             bitstruct.pack('u64', int(steamid_unparsed)))

        if instance == 1:
            instance = 0
            account_number = int(account_number / 2)

        return SteamID(account_number, instance, steam_type, universe)


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


def validate_uuid4(uuid_string):

    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.

    https://gist.github.com/ShawnMilo/7777304
    """

    try:
        val = UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False

    # If the uuid_string is a valid hex code,
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a
    # valid uuid4. This is bad for validation purposes.

    return val.hex == uuid_string