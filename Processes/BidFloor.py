import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_bidfloor = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["auction"].has_key("bidrequests"):
                for bidreq in entry["auction"]["bidrequests"]:
                    if bidreq.has_key("impressions"):
                        for imp in bidreq["impressions"]:
                            bidfloor = round(imp["bidfloor"], 2)
                            if dict_bidfloor.has_key(bidfloor):
                                dict_bidfloor[bidfloor] += 1
                            else:
                                dict_bidfloor.update({bidfloor:1})
    return dict_bidfloor


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "bidfloors")
