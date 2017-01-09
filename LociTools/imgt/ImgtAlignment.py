#! /usr/bin/env python

import re

from collections import defaultdict

from pbcore.io import FastaRecord, FastaWriter


class ImgtAlignment( object ):

    AS_REF    = '-'
    IS_INSERT = '.'

    def __init__( self, locus, handle ):
        self._locus = locus
        self._first = None
        self._dict  = self.__parse_file( handle )
        self._update_alignments()

    def __parse_file( self, handle ):
        """Read the raw alignment data, as is in the file"""
        data = defaultdict(str)
        for line in handle:

            # Skip empty lines and headers
            parts = line.strip().split()
            if len(parts) <= 1:
                continue
            id = parts[0]

            # Only process recognizable sequence alignments
            if id.startswith(locus + "*"):
                substr = ''.join(parts[1:])
                data[id] += substr

                if self._first is None:
                    self._first = id
        return data

    def _update_alignments(self):
        """
        Update same-as-reference positions in the alignments
        with the actual expected base in the reference
        """
        ref_seq = self._dict[self._first]
        data = {self._first: ref_seq}
        for allele, seq in self._dict.iteritems():
            if allele == self._first:
                continue

            # Catch un-even seq lengths, mainly C*04:09N
            if len(ref_seq) == len(seq):
                suffix = ""
            else:
                print "WARNING: uneven lengths for {0}".format(allele)
                suffix  = seq[len(ref_seq):]
                seq     = seq[:len(ref_seq)]
                assert len(ref_seq) == len(seq)

            # If the query sequence is anything other than the
            #  same-as-reference placeholder character or the
            #  insertion character, replace it
            new_seq = ''.join([b if b != self.AS_REF else r
                                   for r, b in zip(ref_seq, seq)])

            data[allele] = new_seq + suffix

        self._dict = data

    def Write( self ):
        """Write out the data to the desired form"""
        raise NotImplementedError("You need to define a Write method!")


class ImgtGenomicAlignment( ImgtAlignment ):

    def __init__( self, *args, **kwargs ):
        super(ImgtGenomicAlignment, self).__init__( *args, **kwargs )

    def Write( self ):
        """Clean-up the sequences and write out a Genomic Fasta"""
        filename = "{0}_genomic.fasta".format( self._locus )
        with FastaWriter( filename ) as handle:
            for allele, seq in self._dict.iteritems():
                # Remove inserts, exon/intron boundaries, and trimmed regions
                seq = re.sub("[.|*]", "", seq)
                record = FastaRecord( allele, seq )
                handle.writeRecord( record )


class ImgtNucleotideAlignment( ImgtAlignment ):
    """
    It's a stupid name, but this is to be consistent with how IMGT labels
    their cDNA alignments
    """

    def __init__( self, *args, **kwargs ):
        super(ImgtNucleotideAlignment, self).__init__( *args, **kwargs )

    def Write( self ):
        """Clean-up the sequences and write out a Genomic Fasta"""

        sets    = []
        writers = []

        for allele, seq in self._dict.iteritems():
            exons = seq.split("|")

            while len(writers) < len(exons):
                fasta = "{0}_exon{1}.fasta".format(self._locus, len(writers) + 1)
                writers.append( FastaWriter(fasta) )
                sets.append( set() )

            for i, exon in enumerate(exons):
                exon = re.sub("[.|*]", "", exon)
                if len(exon) == 0:
                    continue

                if exon in sets[i]:
                    continue
                record = FastaRecord( allele, exon )
                writers[i].writeRecord( record )
                sets[i].add( exon )
