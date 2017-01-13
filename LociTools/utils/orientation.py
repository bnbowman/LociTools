#! /usr/bin/env python

import logging

from LociTools.io.BlasrIO import BlasrReader
import LociTools.utils.utils as utils

log = logging.getLogger(__name__)

__all__ = ["orientSequences"]

def _getOutputFile( inputFile ):
    """
    Get the output file, either as provided or from the input filename
    """
    basename = '.'.join( inputFile.split('.')[:-1] )
    inputType = utils.getFileType( inputFile )
    return '%s.oriented.%s' % (basename, inputType)

def _getOutputType( outputFile ):
    """
    Get the output filetype and confirm the format is valid
    """
    outputType = utils.getFileType( outputFile )
    if outputType in ['fasta', 'fastq']:
        return outputType
    else:
        msg = "Output file must be either FASTA or FASTQ format"
        log.error( msg )
        raise TypeError( msg )

def _identifyReversedRecords( alignFile ):
    """
    Identify hits where the query and reference have difference orientations
    """
    reversedIds = []
    for record in BlasrReader( alignFile ):
        if record.qstrand != record.tstrand:
            reversedIds.append( record.qname )
    return set(reversedIds)

def _orientRecords( records, reversedIds ):
    """
    Reverse-comeplement the records specified in a list
    """
    oriented = []
    for record in records:
        name = record.name.split()[0]
        if name in reversedIds:
            oriented.append( record.reverseComplement() )
        else:
            oriented.append( record )
    return oriented

def orientSequences( inputFile, alignFile, outputFile=None ):
    """
    Reorient a fasta file so all sequences are in the same direction as their reference
    """
    log.info("Reorienting all sequences in %s to the direction of their reference" % inputFile)
    # Set the output file and type
    outputFile = outputFile or _getOutputFile( inputFile )
    outputType = _getOutputType( outputFile )

    if utils.isValidFile( outputFile ):
        log.info("Found existing output file %s, skipping orientation step" % outputFile)
        return outputFile

    # Check the input files, and align the input file if needed
    reversedIds = _identifyReversedRecords( alignFile )
    records = utils.readSequenceRecords( inputFile )
    orientedRecords = _orientRecords( records, reversedIds )

    utils.writeSequenceRecords( outputFile, orientedRecords, outputType )
    return output_file
