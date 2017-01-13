
import os
import os.path as op
import shutil
import logging

from pbcore.io import FastaReader, FastqReader, FastaWriter, FastqWriter

log = logging.getLogger(__name__)

def isValidFile( filepath ):
    return op.exists( filepath ) and op.isfile( filepath )

def isValidDirectory( dirpath ):
    return op.exists( dirpath ) and op.isdir( dirpath )

def isFastaFile( filename ):
    fn = filename.lower()
    if fn.endswith('.fa') or fn.endswith('.fasta'):
        return True
    return False

def isFastqFile( filename ):
    fn = filename.lower()
    if fn.endswith('.fastq') or fn.endswith('.fq'):
        return True
    return False

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

def isExe( file_path ):
    if file_path is None:
        return False
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def which(program):
    """
    Find and return path to local executables
    """
    fpath, fname = os.path.split(program)
    if fpath:
        if isExe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exeFile = os.path.join(path, program)
            if isExe(exeFile):
                return exeFile
    return None

def removeFile( filepath ):
    if isValidFile( filepath ):
        try:
            os.remove( filepath )
        except:
            basename = op.basename( filepath )
            msg = 'Could not delete file "{0}"!'.format(basename)
            log.error( msg )
            raise IOError( msg )

def fastaRecordCount( filepath ):
    try:
        return len(list(FastaReader(filepath)))
    except:
        return None

def getFileType( filename ):
    if filename.endswith('.fa') or filename.endswith('.fasta'):
        return 'fasta'
    elif filename.endswith('.fq') or filename.endswith('.fastq'):
        return 'fastq'
    elif filename.endswith('.fofn'):
        return 'fofn'
    elif filename.endswith('.bas.h5') or filename.endswith('.bax.h5'):
        return 'bas.h5'
    else:
        msg = 'File is not of a recognized filetype'
        log.error( msg )
        raise TypeError( msg )

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
