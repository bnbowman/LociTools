
import os
import os.path as op
import pkg_resources as pkg

from pbcore.io import FastaReader, FastaWriter

from .version import parse_version_str
from .date import parse_date_str

## Private Constant variables

_REF_DIR        = "LociTools.references"
_REF_PATH       = pkg.resource_filename(_REF_DIR, '')
_VERSION_REF    = pkg.resource_filename(_REF_DIR, 'version.txt')
_DATE_REF       = pkg.resource_filename(_REF_DIR, 'date.txt')
_GENOMIC_REF    = pkg.resource_filename(_REF_DIR, 'genomic.fasta')
_GENOMIC_SUFFIX = "gen"
_CDNA_REF       = pkg.resource_filename(_REF_DIR, 'cDNA.fasta')
_CDNA_SUFFIX    = "nuc"
_EXON_REF       = pkg.resource_filename(_REF_DIR, 'exon.map')

## Reference Exceptions

class ReferenceException(Exception):
    pass

class ReferenceFormatException(ReferenceException):
    pass

class MissingReferenceException(ReferenceException):
    pass

class ReferenceIOException(ReferenceException):
    pass


## Private utility functions

def _file_exists( filepath ):
    return op.exists( filepath ) and op.isfile( filepath )

def _dir_exists( dirpath ):
    return op.exists( dirpath ) and op.isdir( dirpath )

def _read_fasta( filepath ):
    """
    Attempt to read a reference FASTA into memory as a list of records
    """
    try:
        recs = list(FastaReader(filepath))
    except:
        raise ReferenceFormatException('Reference file "{0}" is not a well-formated FASTA file!'.format( filepath ))
    return recs

def _write_fasta( filepath, records ):
    """
    Attempt to write a list of records to a new reference FASTA
    """
    try:
        with FastaWriter( filepath ) as handle:
            for record in records:
                handle.writeRecord( record )
    except:
        raise ReferenceIOException('Unable to write reference FASTA "{0}"'.format( filepath ))

def _write_map( filepath, data ):
    """
    Attempt to write a map of files to a new reference map
    """
    try:
        with open( filepath, 'w' ) as handle:
            for key in sorted(data.keys()):
                path = data[key]
                handle.write("{0}\t{1}\n".format(key, path))
    except:
        raise ReferenceIOException('Unable to write reference map "{0}"'.format( filepath ))

def _make_reference( output_path, type_suffix ):
    recs = []
    for resource in pkg.resource_listdir(_REF_DIR, ''):
        if pkg.resource_isdir(_REF_DIR, resource ):
            expected_file = "{0}_{1}.fasta".format(resource, type_suffix)
            expected_path = op.join(_REF_PATH, resource, expected_file)
            if op.exists( expected_path ):
                recs += _read_fasta( expected_path )
            else:
                raise MissingReferenceException('Missing expected reference file "{0}" for Locus "{1}"'.format(expected_file, resource))
    _write_fasta( output_path, recs )
    return True

def _make_exon_map( output_path, locus ):
    data = {}
    exon_dir = op.join( _REF_PATH, locus, "exons" )
    if _dir_exists( exon_dir ):
        for filename in os.listdir( exon_dir ):
            if filename.endswith(".fasta"):
                filepath = op.join( exon_dir, filename )
                exon = int(filename[:-6].split('exon')[-1])
                data[exon] = filepath
    else:
        raise MissingReferenceException('Missing exon data for Locus "{0}"'.format(locus))
    _write_map( output_path, data )
    return True

## Public accessor functions

def genomic_reference_exists():
    return _file_exists( _GENOMIC_REF )

def cDNA_reference_exists():
    return _file_exists( _CDNA_REF )

def exon_reference_exists():
    return _file_exists( _EXON_REF )

def make_genomic_reference():
    return _make_reference( _GENOMIC_REF, _GENOMIC_SUFFIX )

def make_cDNA_reference():
    return _make_reference( _CDNA_REF, _CDNA_SUFFIX )

def make_exon_reference():
    data = {}
    for resource in pkg.resource_listdir(_REF_DIR, ''):
        if pkg.resource_isdir(_REF_DIR, resource ):
            expected_file = "{0}_exons.map".format(resource)
            expected_path = op.join(_REF_PATH, resource, expected_file)
            if op.exists( expected_path ):
                data[resource] = expected_path
            elif _make_exon_map( expected_path, resource ):
                data[resource] = expected_path
            else:
                raise MissingReferenceException('Missing expected reference file "{0}" for Locus "{1}"'.format(expected_file, resource))
    _write_map( _EXON_REF, data )
    return True

def get_reference_version():
    print parse_version_str( "3.26.0" )

def get_reference_date():
    print parse_date_str( "1983 September 17" )

def get_genomic_reference():
    if genomic_reference_exists():
        return _GENOMIC_REF
    elif make_genomic_reference():
        return _GENOMIC_REF
    else:
        raise MissingReferenceException('Unable to generate Genomic reference FASTA')

def get_cDNA_reference():
    if cDNA_reference_exists():
        return _CDNA_REF
    elif make_cDNA_reference():
        return _CDNA_REF
    else:
        raise MissingReferenceException('Unable to generate cDNA reference FASTA')

def get_exon_reference():
    if exon_reference_exists():
        return _EXON_REF
    elif make_exon_reference():
        return _EXON_REF
    else:
        raise MissingReferenceException('Unable to generate exon reference map')
