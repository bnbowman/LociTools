#! /usr/bin/env python

# Author: Brett Bowman

from __future__ import absolute_import

import logging
import itertools
import time

from pbcore.io import openDataSet

from LociTools import options
from LociTools.options import Applications
from LociTools import references
from LociTools.imgt.ImgtReference import ImgtReference
from LociTools.typing import LociTyper

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

def main():
    options.parseOptions()
    app = options.whichApplication()
    if app == Applications.TYPING:
        log.debug("Typing")
        print references.genomicReference()
        print references.cDNAReference()
        print references.exonReference()
        typer = LociTyper("all")
        print typer.genomicRef
        print typer.cDnaRef
        print typer.exonRef
        typer( options.options.typingQuery )
    elif app == Applications.ANALYSIS:
        log.debug("Analysis")
    elif app == Applications.UPDATE:
        log.debug("Update")
        references.get_reference_version()
        references.get_reference_date()
        imgt = ImgtReference( options.options.imgtAlignmentZip )
    log.debug("Done")

if __name__ == "__main__":
    main()
