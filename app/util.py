from valve.steam.id import SteamID
import bitstruct
import requests
from uuid import UUID
import sys

from . import app

if sys.version_info > (3,):
    long = int

auth_url = app.config['STEAM_API_BACKEND_URL'] + 'ISteamUserAuth/AuthenticateUserTicket/v0001'


def build_steamid(steamid_unparsed):
    if str(steamid_unparsed).isdigit():
        universe, steam_type, instance, account_number = bitstruct.unpack('u8u4u20u32',
                             bitstruct.pack('u64', long(steamid_unparsed)))

        # Bit confusing, but convert from ID64 to STEAM_0:A:B format
        # See https://developer.valvesoftware.com/wiki/SteamID
        instance = 0
        if account_number % 2 == 1:
            instance = 1
            account_number -= 1
        account_number = long(account_number / 2)

        return SteamID(account_number, instance, steam_type, universe)

    return SteamID.from_text(steamid_unparsed)


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
    r.raise_for_status()

    resp = r.json()

    try:
        response = resp['response']

        if 'params' in response:
            params = resp['response']['params']
            if params['result'] != 'OK':
                return None

            return build_steamid(params['steamid'])
        elif 'error' in response:
            error = response['error']
            # Invalid ticket case
            if error['errorcode'] == 101:
                return None
    except KeyError:
        # Fallthrough to exception
        pass

    raise Exception('Unexpected response from %s:\n%s' % (auth_url, resp))


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
