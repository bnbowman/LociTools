#! /usr/bin/env python

# Author: Brett Bowman

from __future__ import absolute_import

import logging
import itertools
import time

from pbcore.io import openDataSet

from LociTools import options
from LociTools.options import Applications
from LociTools.typing import LociTyper

def main():
    log = logging.getLogger()
    options.parseOptions()
    app = options.whichApplication()
    if app == Applications.TYPING:
        print "Typing"
        typer = LociTyper("all")
        print typer.genomicRef
        print typer.cDnaRef
        print typer.exonRef
    elif app == Applications.ANALYSIS:
        print "Analysis"
    elif app == Applications.UPDATE:
        print "Update"
    

if __name__ == "__main__":
    main()
