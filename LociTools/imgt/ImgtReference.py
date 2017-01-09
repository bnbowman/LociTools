#! /usr/bin/env python

import sys
import zipfile
import os
import re

import logging
from collections import defaultdict

from pbcore.io import FastaRecord, FastaWriter

from .ImgtAlignment import ImgtGenomicAlignment, ImgtNucleotideAlignment

LOCUS_LIST = ["A", "B", "C"]
GEN_SUFFIX = "_gen.txt"
NUC_SUFFIX = "_nuc.txt"

log = logging.getLogger(__name__)

class ImgtReference(object):

    def __init__( self, filename ):
        """
        Verify the input is a well-formed zip archive at creation
        """
        # Check that our input is a proper Zip archive before opening
        log.info('Loading IMGT Reference dataset from "{0}"'.format(os.path.basename(filename)))
        assert filename.endswith(".zip")
        assert zipfile.is_zipfile( filename )
        self._zip = zipfile.ZipFile( filename )
        self.__validate()
        self.__read_metadata()

    def __validate(self):
        """
        Validate that we have both genomic and nucleotide references for
        all desired loci
        """
        gen_count = 0
        nuc_count = 0
        counts = defaultdict(int)
        for filename in self._zip.namelist():
            base = os.path.basename(filename)
            locus = base.split('_')[0]
            if locus not in LOCUS_LIST:
                continue
            counts[locus] += 1
            if base.endswith(GEN_SUFFIX):
                gen_count += 1
            elif base.endswith(NUC_SUFFIX):
                nuc_count += 1
        # We should have an equal number of Genomic and Nucleotide files,
        #  and 2-3 per locus (w/ or w/o protein encodings)
        assert gen_count == nuc_count
        for locus, count in counts.iteritems():
            assert count in [2, 3]

    def __read_metadata(self):
        filenames = [f for f in self._zip.namelist() if f.endswith(".txt")]
        with self._zip.open(filenames[0]) as handle:
            handle.next()
            self._version_str = handle.next().split(':')[-1].strip()
            self._date_str = handle.next().split(':')[-1].strip()
        log.info('Found data from IMGT release version "{0}"'.format(self._version_str))
        log.info('IMGT data is dated "{0}"'.format(self._date_str))

    @property
    def version(self):
        return self._version_str

    @property
    def date(self):
        return self._date_str

    def writeMetadata(self):
        pass

    def updateGenomicReference(self):
        for filename in self._zip.namelist():
            base   = os.path.basename(filename)
            locus = base.split('_')[0]
            if locus not in LOCUS_LIST:
                continue
            if base.endswith(GEN_SUFFIX):
                log.info("Processing {0} for genomic data from locus: {1}".format(base, locus))
                aln = ImgtGenomicAlignment( locus, z.open(filename) )
                aln.Write()

    def updateCDNAReference(self):
        pass

"""
with zipfile.ZipFile(sys.argv[1]) as z:
    for filename in z.namelist():
        base   = os.path.basename(filename)
        locus = base.split('_')[0]
        if locus not in LOCUS_LIST:
            continue
        if base.endswith(GEN_SUFFIX):
            print "Processing {0} for genomic data from locus: {1}".format(base, locus)
            aln = ImgtGenomicAlignment( locus, z.open(filename) )
            aln.Write()
        elif base.endswith(NUC_SUFFIX):
            print "Processing {0} for cDNA data from locus: {1}".format(base, locus)
            aln = ImgtNucleotideAlignment( locus, z.open(filename) )
            aln.Write()
"""
