#! /usr/bin/env python

import logging
from operator import itemgetter
from collections import defaultdict

from pbcore.io.FastqIO import FastqWriter

from LociTools import utils
from LociTools.io import BlasrReader

log = logging.getLogger(__name__)

VALID_METHODS = ['barcode', 'locus', 'both', 'all']
VALID_SORTS   = ['reads', 'accuracy', 'best', 'none']
VALID_LOCI    = ['A', 'B', 'C', 'DPA1', 'DPB1', 'DQA1', 'DQB1', 'DRB1', 'DQB1']

DEFAULT_NPROC = 8
DEFAULT_LOCI = ['A', 'B', 'C', 'DPA1', 'DPB1', 'DQA1', 'DQB1', 'DRB1', 'DQB1']
DEFAULT_METHOD = 'locus'
DEFAULT_SORT = 'accuracy'
DEFAULT_MIN_FRAC = 0.15

class SequenceSelector( object ):

    def __init__(self, method=DEFAULT_METHOD,
                       sort=DEFAULT_SORT,
                       loci=DEFAULT_LOCI,
                       minFraction=DEFAULT_MIN_FRAC):
        self.method = method
        self.sort = sort
        self.loci = loci
        self.minFraction = minFraction

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, arg):
        if arg in VALID_METHODS:
            self._method = arg
        else:
            msg = "Invalid record grouping method: %s" % arg
            log.error( msg )
            raise ValueError( msg )

    @property
    def sort(self):
        return self._sort

    @sort.setter
    def sort(self, arg):
        if arg in VALID_SORTS:
            self._sort = arg
        else:
            msg = "Invalid record grouping method: %s" % arg
            log.error( msg )
            raise ValueError( msg )

    @property
    def loci(self):
        return self._loci

    @loci.setter
    def loci(self, args):
        self._loci = []
        if isinstance(args, list):
            for arg in args:
                if arg in VALID_LOCI:
                    self._loci.append( arg )
        elif args in VALID_LOCI:
            self._loci.append( args )
        if len(self._loci) == 0:
            msg = "No valid loci supplied" % arg
            log.error( msg )
            raise ValueError( msg )

    @property
    def minFraction(self):
        return self._minFrac

    @minFraction.setter
    def minFraction(self, arg):
        if isinstance(arg, float):
            self._minFrac = arg
        else:
            msg = "Invalid minFraction: must be 'float' but got '{0}' ".format(type(arg))
            log.error( msg )
            raise ValueError( msg )

    def _groupAlignmentsByLocus( self, alignments ):
        """Group sequences by the locus of their best alignment"""
        groups = defaultdict(list)
        for record in alignments:
            reference = record.tname.split('*')[0]
            locus = reference.split('_')[-1]
            if locus not in self.loci:
                continue
            groups[locus].append( record )
        return groups

    def _groupAlignmentsByBarcode( self, alignments ):
        """Group sequences by their barcode"""
        groups = defaultdict(list)
        for alignment in alignments:
            name = alignment.qname
            if name.startswith('Barcode'):
                name = name[7:]
            if name.startswith('_'):
                name = name[1:]
            barcode = name.split('_Cluster')[0]
            groups[barcode].append( alignment )
        return groups

    def _groupAlignmentsByBoth( self, alignments ):
        """Return all sequences as their own group"""
        groups = {}
        bcGroups = self._groupAlignmentsByBarcode( alignments )
        for barcode, bcAligns in bcGroups.iteritems():
            locusGroups = self._groupAlignmentsByLocus( bcAligns, loci )
            for locus, locusAligns in locusGroups.iteritems():
                groupName = '%s_%s' % (barcode, locus)
                groups[groupName] = locusAligns
        return groups

    def _groupAlignmentsByAll( self, alignments ):
        """Treat each sequence as their own group"""
        return {a.qname: [a] for a in alignments}

    def _groupAlignments( self, alignments ):
        """
        Group alignments in the user-specified way
        """
        log.debug('Grouping sequences with method "%s"' % self.method)
        if self.method == 'locus':
            return self._groupAlignmentsByLocus( alignments )
        elif self.method == 'barcode':
            return self._groupAlignmentsByBarcode( alignments )
        elif self.method == 'both':
            return self._groupAlignmentsByBoth( alignments )
        elif self.method == 'all':
            return self._groupAlignmentsByAll( alignments )
        else:
            msg = "Invalid Selection Metric: %s" % method
            log.error( msg )
            raise ValueError( msg )

    def _sortGroups( self, sequences, groups ):
        """Order each group of records individually"""
        log.debug('Sorting sequences with method "%s"' % self.sort)
        # Generate a dictionary of sorting
        if self.sort == 'reads':
            data = {s.name: utils.recordSupport(s) for s in sequences}
        elif self.sort == 'accuracy':
            data = {s.name: utils.recordAccuracy(s) for s in sequences}
        elif self.sort == 'none':
            data = {s.name: 1 for s in sequences}
        elif self.sort == 'best':
            data = None
        else:
            msg = "Invalid Sorting Metric: %s" % sort
            log.error( msg )
            raise ValueError( msg )

        ordered = {}
        for groupName, group in groups.iteritems():
            sortedRecords = sorted( group, key=lambda x: data[x.qname], reverse=True )
            ordered[groupName] = sortedRecords
        return ordered

    def _selectSequences( self, sequences, groups ):
        """Select the top 1-2 sequences for each Locus"""

        selectedIds = []
        for group in groups.itervalues():

            # Take the first sequence from each group
            first, rest = group[0], group[1:]
            selectedIds.append( first.qname )
            firstReads = utils.getNumReads( first.qname )

            # Take the second sequence with a different reference
            for record in rest:
                numReads = utils.getNumReads( record.qname )
                if record.tname == first.tname and record.nmis == first.nmis:
                    firstReads += utils.getNumReads( record.qname )
                elif numReads > (firstReads * self.minFraction):
                    selectedIds.append( record.qname )
                    break

        selected = [s for s in sequences if s.id in selectedIds]
        log.info('Selected %s sequences from %s total for further analysis' % (len(selected), len(sequences)))
        return selected

    def __call__(self, inputFile, outputFile=None, alignFile=None):
        """Pick the consensus seqs per group from a sequence file"""

        # Read the input sequences and use them to generate our sorting data
        sequences = utils.readSequenceRecords( inputFile )

        # Set the output file if not specified
        outputFile = outputFile or utils.getOutputFile( inputFile, 'selected' )
        outputType = utils.getFileType( outputFile )

        # Group, sort, and select the sequences to be analyzed
        alignments = list( BlasrReader( alignFile ))
        groups = self._groupAlignments( alignments )
        sortedGroups = self._sortGroups( sequences, groups )
        selected = self._selectSequences( sequences, sortedGroups )

        # Write the selected sequences out to file and return
        utils.writeSequenceRecords( outputFile, selected, outputType )
        return outputFile
