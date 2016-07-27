import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_format = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            if entry["auction"].has_key("bidrequests"):
                for bidreq in entry["auction"]["bidrequests"]:
                    if bidreq.has_key("impressions"):
                        for imp in bidreq["impressions"]:
                            format = imp["format"]
                            if dict_format.has_key(format):
                                dict_format[format] += 1
                            else:
                                dict_format.update({format:1})
    return dict_format


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "formats")
