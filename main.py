#!/usr/bin/env python3
"""Optimize a small synthetic travel itinerary under explicit budget and day constraints."""
import argparse
import itertools
import json
from pathlib import Path


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(name + " must be an integer >= " + str(minimum))
    return value
