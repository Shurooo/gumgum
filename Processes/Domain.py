import json
import Get_Result_Output as gro


result_list = []


def run(addr_in):
    dict_domain = {}
    with open(addr_in, "r") as file_in:
        for line in file_in:
            entry = json.loads(line)
            domain = (entry["auction"]["site"]["domain"])
            if (domain == None) or (len(domain) == 0):
                domain = "NONE"
            domain_tmp = domain.split("www.")
            domain = domain_tmp[len(domain_tmp)-1]
            if dict_domain.has_key(domain):
                dict_domain[domain] += 1
            else:
                dict_domain.update({domain:1})
    return dict_domain


def add_result(result):
    result_list.append(result)


def get_result():
    gro.get_result(result_list, "domains")
