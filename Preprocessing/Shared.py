"""
Define some shared functions for all methods that process JSON objects that represent impressions.
"""

import os
import json

# The folder that contains the lists of possible values used to process certain features.
dicts_root_ = "dicts"


def get_dict(var):
    """
    Get and return the list of possible values to process the given variable.
    :param var: the variable
    :return: the list of possible values needed to process the given variable
    """
    with open(os.path.join(dicts_root_, "dict_"+var+".txt"), "r") as file_in:
        dict_var = [line.rstrip("\r\n") for line in file_in]
    return dict_var


def get_dict_json(var):
    """
    Get and return the dictionary stored in JSON format to process the given variable.
    :param var: the variable
    :return: the dictionary stored in JSON format that is needed to process the given variable
    """
    with open(os.path.join(dicts_root_, var), "r") as file_in:
        return json.load(file_in)


def binarize(result, index, length):
    """
    Given the index of the value that a variable takes in a list of possible values for the variable, and the length of the list,
    creates an amount of boolean variables that equal to the length, and set the boolean variable at the corresponding index to 1.
    In the end, add the boolean varaibles to the list of parsed results.
    :param result: the list of parsed results
    :param index: the index of the value that a variable takes in a list of possible values for the variable
    :param length: the length of the list of possible values for the variable
    :return: None
    """
    # Index should never be negative
    if index < 0:
        raise IndexError

    binary_var = [0]*length
    binary_var[index] = 1
    result.extend(binary_var)


def add_to_result(result, var, dict_var):
    """
    Given a variable with a specific value and a list of possible values for this variable,
    get the index of the specific value in the list, and call binarize() to parse the value and add it to the list of parsed results.
    :param result: the list of parsed results
    :param var: the value of the variable to be parsed
    :param dict_var: the list of possible values of the variable
    :return: None
    """
    try:
        index = dict_var.index(var)
    except:
        # If the given value is not in the list, set the index to be the length of the list
        index = len(dict_var)
    binarize(result, index, len(dict_var)+1)
