import Event
import Auction
import Auction_Site
import Auction_BidRequests


def process(entry, result):
    Event.process(entry, result)
    margin = Auction.process(entry, result)
    Auction_Site.process(entry,result)
    Auction_BidRequests.process(margin, entry, result)
    # Response
    result.append(entry["response"])
