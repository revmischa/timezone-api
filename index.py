import json
from timezones import common_timezones_useful, TZList  # noqa
from geolite2 import geolite2


def handler(event, context):
    """Return list of common timezones suitable for display."""
    ip = event['requestContext']['identity']['sourceIp']
    reader = geolite2.reader()
    geoip = reader.get(ip)

    # try to get user's country
    country: str = None
    tz_guess: str = None

    params = event['queryStringParameters']
    restrict_to_country: bool = False  # should we only show timezones from this country

    if geoip:
        if geoip.location:
            tz_guess = geoip.location.time_zone
        if geoip.country:
            country = geoip.country.iso_code

    tzs: TZList = common_timezones_useful(country=country)

    # add field for searching on
    for tz in tzs:
        cc: str = tz['code']
        searchable: str = f"{tz['country_name']} {tz['name']} {tz['continent']}"
        if cc == 'US':
            # make 'USA' work
            searchable += " usa"
            tz['searchable'] = searchable

    data = dict(
        location=tz_guess,
        list=tzs,
    )

    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {
                "Cache-Control": "private, max-age=86400",
                'Content-Type': 'application/json'
            }}
