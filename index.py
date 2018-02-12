import json
from timezones import common_timezones_useful
from geolite2 import geolite2


def handler(event, context):
    """Return list of common timezones suitable for display."""
    ip = event['requestContext']['identity']['sourceIp']
    reader = geolite2.reader()
    geoip = reader.get(ip)

    # try to get user's country
    country = ""
    tz_guess = ""

    params = event['queryStringParameters'] or {}
    restrict_to_country = 'country_restrict' in params and params['country_restrict']  # should we only show timezones from this country

    if geoip:
        if geoip.location:
            tz_guess = geoip.location.time_zone
        if geoip.country:
            country = geoip.country.iso_code

    tzs = common_timezones_useful(country=country)

    # add field for searching on
    for tz in tzs:
        cc = tz['code']
        searchable = f"{tz['country_name']} {tz['name']} {tz['continent']}"
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
