import json
import Get_Result_Output as gro


result_list = []


def get_dates():
    may = [(5, i, j) for i in range(1, 8) for j in range(24)]
    # may = []
    june = [(6, i, j) for i in range(4, 26) for j in range(24)]
    # june = []
    return may+june


def run(addr_in):
    dict_banner = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["auction"].has_key("bidrequests"):
                for bidreq in entry["auction"]["bidrequests"]:
                    if bidreq.has_key("impressions"):
                        for imp in bidreq["impressions"]:
                            if imp.has_key("banner"):
                                w = imp["banner"]["w"]
                                h = imp["banner"]["h"]
                                key = (w, h)
                            else:
                                key = "None"

                            if dict_banner.has_key(key):
                                dict_banner[key] += 1
                            else:
                                dict_banner.update({key:1})
    return dict_banner


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "banners")
