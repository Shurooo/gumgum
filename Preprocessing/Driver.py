"""
Provide a driver of the methods that process impressions represented by JSON objects formatted by Extractor.py.
"""

import Event
import Auction
import Auction_Site
import Auction_BidRequests


def process(entry, result, mode="Num"):
    """
    Given a JSON object formatted by Extractor.py, parse each key-value pair in the object.
    :param entry: the JSON object that represents one impression
    :param result: the buffer to store the parsed variables
    :param mode: "Num" or "Bin"; a flag indicating whether to parse bid bloor into binary variables or just keep the numerical value
    :return: a list containing parsed variables of an impression
    """

    Event.process(entry, result)
    margin = Auction.process(entry, result)
    Auction_Site.process(entry, result)
    Auction_BidRequests.process(margin, entry, result, mode)

    # Response
    result.append(entry["response"])


def get_header():
    """
    Get the names of the features in the list returned by process().
    Each item is a tuple where the first element is the feature name and the second element is the number of variables that feature contains.
    :return: a list of tuples containing the feature names and the lengths of the corresponding features
    """
    header = []
    header.extend(Event.get_header())
    header.extend(Auction.get_header())
    header.extend(Auction_Site.get_hearder())
    header.extend(Auction_BidRequests.get_hearder())
    header.append(("response", 1))

    return header

