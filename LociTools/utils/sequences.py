
import os
import os.path as op
import shutil
import logging

from pbcore.io import FastaReader, FastqReader, FastaWriter, FastqWriter

from .utils import isValidFile, isFastaFile, isFastqFile, getFileType

log = logging.getLogger(__name__)

def isValidFasta( filename ):
    if not isValidFile( filename ) or not isFastaFile( filename ):
        return False
    try:
        list(FastaReader(filename))
    except:
        return False
    return True

def isValidFastq( filename ):
    if not isValidFile( filename ) or not isFastqFile( filename ):
        return False
    try:
        list(FastqReader(filename))
    except:
        return False
    return True

def fastaRecordCount( filepath ):
    try:
        return len(list(FastaReader(filepath)))
    except:
        return None

def readSequenceRecords( filename ):
    """
    Parse the input sequence records with the appropriate pbcore Reader
    """
    fileType = getFileType( filename )
    if fileType == 'fasta':
        return list( FastaReader( filename ))
    elif fileType == 'fastq':
        return list( FastqReader( filename ))
    else:
        msg = 'Input file must be either FASTA or FASTQ'
        log.error( msg )
        raise TypeError( msg )

def writeSequenceRecords( filename, records, filetype=None ):
    """
    Write the records out to file
    """
    fileType = filetype or getFileType( filename )
    if fileType == 'fasta':
        with FastaWriter( filename ) as writer:
            for record in records:
                writer.writeRecord( record )
    elif fileType == 'fastq':
        with FastqWriter( filename ) as writer:
            for record in records:
                writer.writeRecord( record )
    else:
        msg = 'Output filetype must be either FASTA or FASTQ'
        log.error( msg )
        raise TypeError( msg )
    return filename

def getNumReads( recordName ):
    assert 'NumReads' in recordName
    return int(recordName.split('NumReads')[1])

def recordSuppot( record ):
    return getNumReads( record.name )

def qualityToP(qv):
    return 1-(10**(-1*float(qv)/10.0))

def recordAccuracy( record, precision=7 ):
    assert hasattr( record, 'quality' )
    pValues = [qualityToP(qv) for qv in record.quality]
    average = sum(pValues)/len(pValues)
    return round(average, precision)
