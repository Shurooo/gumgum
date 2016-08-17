"""
Define the method to parse variables "t", "cc", and "rg"
"""

import Shared as sd
import pytz
from datetime import datetime


countries_ = ["None", "US", "GB", "CA", "DE", "FR", "NL", "IT"]
regions_ = sd.get_dict("region")
region_timezone_ = sd.get_dict_json("region_timezone.json")


def process(entry, result):
    """
    Given a JSON object formatted by Extractor.py, parse variables "t", "cc", and "rg", and the results to the list of possible results.
    :param entry: the JSON object that represents one impression
    :param result: the list of possible results
    :return: None
    """

    # Event - time
    t = entry["t"] / 1000   # Divide t by 1000 because the unit of measurement is 1 millisecond for t

    # Get the UTC time from the timestamp, and parse minute of the hour, hour of the day, and day of the week
    utc_t = datetime.utcfromtimestamp(t)
    min = utc_t.minute
    sd.binarize(result, min, 60)
    hour = utc_t.hour
    sd.binarize(result, hour, 24)
    day = utc_t.weekday()
    sd.binarize(result, day, 7)

    # Determine if it is weekend
    if day == 5 or day == 6:
        result.append(1)
    else:
        result.append(0)

    # Determine if it is Friday or Saturday
    if day == 4 or day == 5:
        result.append(1)
    else:
        result.append(0)

    try:
        # Try to local time using UTC time and country and region

        # Determine time zone using country and region
        country = entry["cc"]
        if country in ["US", "CA", "AU"]:
            tz = pytz.timezone(region_timezone_[entry["rg"]])
        else:
            tz = pytz.timezone(pytz.country_timezones(country)[0])

        # Get hour of the day and day of the week in local time
        local_t = tz.normalize(utc_t.astimezone(tz))
        local_hour = local_t.hour
        sd.binarize(result, local_hour, 24)
        local_day = local_t.weekday()
        sd.binarize(result, local_day, 7)
    except:
        # If local time cannot be extracted, set all variables in this section to be 0
        result.extend([0]*31)

    # Event - country
    sd.add_to_result(result, entry["cc"], countries_)

    # Event - region
    sd.add_to_result(result, entry["rg"], regions_)


def get_header():
    """
    Return the names of features extracted in this section, and the number of variables used to represent each feature.
    :return: a list of tuples containing the feature names and the lengths of the corresponding features
    """
    minute = ("minute", 60)
    hour = ("hour", 24)
    day = ("day", 7)
    weekend = ("weekend", 1)
    fri_or_sat = ("fri_or_sat", 1)
    local_hour = ("local_hour", 24)
    local_day = ("local_day", 7)
    country = ("country", len(countries_)+1)
    region = ("region", len(regions_)+1)

    return [minute, hour, day, weekend, fri_or_sat, local_hour, local_day, country, region]
