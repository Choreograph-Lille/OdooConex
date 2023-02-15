# -*- coding: utf-8 -*-


def clean_dict(my_dict=False):
    if not my_dict:
        return {}
    for k, v in my_dict.items():
        if v is None:
            my_dict[k] = False
    return my_dict
