
import logging
import os
import os.path as op
from enum import Enum

from LociTools import utils
from LociTools import references

log = logging.getLogger(__name__)

class GroupingType(Enum):
    LOCUS = 1
    ALLELE = 2
    BOTH = 3
    ALL = 4


class LociTyper( object ):

    def __init__( self, loci,
                        grouping=GroupingType.BOTH,
                        genomicRef=None,
                        cDnaRef=None,
                        exonRef=None):
        self.version    = references.version()
        self.date       = references.date()
        self.loci       = loci
        self.grouping   = grouping
        self.genomicRef = genomicRef
        self.cDnaRef    = cDnaRef
        self.exonRef    = exonRef

        # Stuff
        print [s.name for s in GroupingType]

    ## Setter / Getter Methods

    @property
    def loci(self):
        return self._loci

    @loci.setter
    def loci(self, arg):
        self._loci = arg

    @property
    def grouping(self):
        return self._grouping

    @grouping.setter
    def grouping(self, arg):
        if isinstance(arg, GroupingType):
            self._grouping = arg
        else:
            raise TypeError("Value for 'grouping' not a valid GroupingType!")

    @property
    def genomicRef(self):
        return self._genomicRef

    @genomicRef.setter
    def genomicRef(self, arg):
        if arg is None:
            self._genomicRef = references.genomicReference()
        else:
            log.debug('Overriding default Genomic Reference FASTA with "{0}"'.format(arg))
            self._genomicRef = arg

    @property
    def cDnaRef(self):
        return self._cDnaRef

    @cDnaRef.setter
    def cDnaRef(self, arg):
        if arg is None:
            self._cDnaRef = references.cDNAReference()
        else:
            log.debug('Overriding default cDNA Reference FASTA with "{0}"'.format(arg))
            self._cDnaRef = arg

    @property
    def exonRef(self):
        return self._exonRef

    @exonRef.setter
    def exonRef(self, arg):
        if arg is None:
            self._exonRef = references.exonReference()
        else:
            log.debug('Overriding default Exon Reference Map with "{0}"'.format(arg))
            self._exonRef = arg

    ## Private methods

    def __validateInput( self, inputArg ):
        """
        Valid the input argument and convert to absolute path
        """
        if utils.isValidDirectory( inputArg ):
            log.info("Input appears to be a directory, looking for analysis FASTQ result")
            contents = os.listdir( inputArg )
            absDir = op.abspath( inputArg )
            if "amplicon_analysis.fastq" in contents:
                absPath = op.join( absDir, "amplicon_analysis.fastq" )
                if utils.isValidFastq( absPath ):
                    return absPath
            elif "loci_analysis.fastq" in contents:
                absPath = op.join( absDir, "loci_analysis.fastq" )
                if utils.isValidFastq( absPath ):
                    return absPath
            else:
                msg = "No valid analysis FASTQ files found in the input directory!"
                log.error( msg )
                raise IOError( msg )
        elif utils.isValidFile( inputArg ):
            if utils.isValidFasta( inputArg ):
                return op.abspath( inputArg )
            elif utils.isValidFastq( inputArg ):
                return op.abspath( inputArg )
            else:
                msg = "Input is not a valid FASTQ or FASTQ file!"
                log.error( msg )
                raise IOError( msg )
        else:
            msg = "Input is not a valid analysis file or directory!"
            log.error( msg )
            raise IOError( msg )

    def __call__(self, inputArg ):
        # Second, get the input file if a directory was specified
        validInput = self.__validateInput( inputArg )
        print "INPUT: ", validInput

        # Finally, run the Typing procedure
        #renamed_file = rename_sequences( sequence_file )
        #raw_alignment = full_align_best_reference( renamed_file, genomic_reference )
        #reoriented = orient_sequences( renamed_file, alignment_file=raw_alignment )
        #selected = extract_alleles( reoriented, alignment_file=raw_alignment,
        #                    method=grouping,
        #                    loci=loci)
        #trimmed = trim_alleles( selected, trim=trim )
        #gDNA_alignment = full_align_best_reference( trimmed, genomic_reference )
        #cDNA_file = extract_cDNA( trimmed, exon_fofn, alignment_file=gDNA_alignment, debug=debug )
        #cDNA_alignment = align_by_identity( cDNA_file, cDNA_reference )
        #typing = summarize_typing( gDNA_alignment, cDNA_alignment )
        #return typing
