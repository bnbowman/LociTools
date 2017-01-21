
import os
import os.path as op
import shutil
import logging

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

def getFileType( filename ):
    if filename.endswith('.fa') or filename.endswith('.fasta'):
        return 'fasta'
    elif filename.endswith('.fq') or filename.endswith('.fastq'):
        return 'fastq'
    elif filename.endswith('.fofn'):
        return 'fofn'
    elif filename.endswith('.bas.h5') or filename.endswith('.bax.h5'):
        return 'bas.h5'
    elif filename.endswith('.m1'):
        return 'm1'
    elif filename.endswith('.m5'):
        return 'm5'
    else:
        msg = 'File is not of a recognized filetype'
        log.error( msg )
        raise TypeError( msg )

def getOutputFile( inputFile, fileTag ):
    """
    Name a new file with the same type as the old, but a new descriptive tag
     before the suffix
    """
    basename = '.'.join( inputFile.split('.')[:-1] )
    fileType = getFileType( inputFile )
    return '%s.%s.%s' % (basename, fileTag, fileType)
