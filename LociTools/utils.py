
import os
import os.path as op
import shutil
import logging

from pbcore.io import FastqReader, FastqWriter, FastqRecord

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

def sequencefiletype( file_list ):
    if all([isFastq(f) for f in file_list]):
        return 'fastq'
    elif all([isFasta(f) for f in file_list]):
        return 'fasta'
    else:
        raise ValueError

def writeFastq( fasta_records, output_file):
    """
    Write a FastaRecord, or list of records, out to file
    """
    with FastqWriter( output_file ) as handle:
        if isinstance( fasta_records, FastqRecord ):
            handle.writeRecord( fasta_records )
        elif isinstance( fasta_records, list):
            for record in fasta_records:
                handle.writeRecord( record )
        else:
            msg = "Input Record(s) type not recognized"
            log.error( msg )
            raise TypeError( msg )
    check_output_file( output_file )


def read_fastq_dict( fastq_input ):
    records = {}
    if isinstance( fastq_input, str ):
        for rec in FastqReader( fastq_input ):
            name = rec.name.strip().split()[0]
            assert name not in records
            records[name] = rec
    elif isinstance( fastq_input, list ):
        for filename in fastq_input:
            for rec in FastqReader( filename ):
                name = rec.name.strip().split()[0]
                assert name not in records
                records[name] = rec
    return records

def getBarcode( record ):
    return record.name.split('_')[0][7:]

def get_file_source( filename ):
    base_name = os.path.basename( filename )
    root_name = base_name.split('.')[0]
    parts = root_name.split('_')
    return parts[1]

def get_base_sequence_name( name ):
    name = name.split()[0]
    if name.endswith('|quiver'):
        name = name.split('|')[0]
    if name.endswith('_cns'):
        name = name[:-4]
    return name

def memoize(function):
    cache = {}
    def decorated_function(*args):
        if args in cache:
            return cache[args]
        else:
            val = function(*args)
            cache[args] = val
            return val
    return decorated_function

def cleanup_directory( directory ):
    for entry in os.listdir( directory ):
        removal_flag = False
        if entry.endswith('aln') or entry.endswith('aln_unsorted'):
            removal_flag = True
        if entry.startswith('tmp_cns_') or entry.startswith('tmp_reads_'):
            removal_flag = True
        if removal_flag:
            try:
                os.remove( os.path.join( directory, entry) )
            except:
                pass

def write_list_file( file_list, output_file ):
    with open(output_file, 'w') as handle:
        for filename in file_list:
            print >> handle, filename

def read_list_file( list_file ):
    list_contents = []
    with open(list_file, 'r') as handle:
        for line in handle:
            value = line.strip().split()[0]
            if value:
                list_contents.append( value )
    return list_contents

def read_dict_file( dict_file ):
    dict_contents = {}
    with open(dict_file, 'r') as handle:
        for line in handle:
            try:
                key, value = line.strip().split()
                dict_contents[key] = value
            except:
                pass
    return dict_contents

def cross_ref_dict( query_dict, ref_dict ):
    new_dict = {}
    for key in query_dict:
        old_value = query_dict[key]
        if old_value.startswith('HLA:'):
            old_value = old_value.split('_')[0]
        try:
            new_value = ref_dict[old_value]
        except:
            new_value = 'N/A'
        new_dict[key] = new_value
    return new_dict

def validate_file( filename ):
    if os.path.isfile( filename ) and (os.path.getsize( filename ) > 0):
        return os.path.abspath( filename )
    return False

# TODO: Replace all instances of this function with the above "validate_file"
def valid_file( filepath ):
    if os.path.isfile( filepath ) and (os.path.getsize( filepath ) > 0):
        return True
    return False

def check_output_file( filepath ):
    if valid_file( filepath ):
        return
    else:
        msg = 'Expected output file not found! "{0}"'.format(filepath)
        log.error( msg )
        raise IOError( msg )

def copy_file( source, destination ):
    shutil.copy( source, destination )
    check_output_file( destination )
    return destination

def remove_file( filepath ):
    if os.path.isfile( filepath ):
        try:
            os.remove( filepath )
        except:
            basename = os.path.basename( filepath )
            msg = 'Could not delete file! "%s"' % basename
            log.error( msg )
            raise IOError( msg )

def is_exe( file_path ):
    if file_path is None:
        return False
    return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

def which(program):
    """
    Find and return path to local executables  
    """
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def create_directory( directory ):
    # Skip if the directory exists
    if os.path.isdir( directory ):
        return
    try: # Otherwise attempt to create it
        os.mkdir( directory )
    except: 
        msg = 'Could not create directory "{0}"'.format(directory)
        log.info( msg )
        raise IOError( msg )

def remove_directory( directory ):
    try:
        shutil.rmtree( directory )
    except OSError:
        log.warn("No directory named '%s' detected for deletion" % directory)
