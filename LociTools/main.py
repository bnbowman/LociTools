#! /usr/bin/env python

# Author: Brett Bowman

from __future__ import absolute_import

import logging
import itertools
import time

from pbcore.io import openDataSet

from LociTools.options import (options, parseOptions)

def main():
    parseOptions()

if __name__ == "__main__":
    main()
