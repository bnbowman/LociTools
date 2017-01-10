
import os
import logging
import calendar
import os.path as op
import pkg_resources as pkg

from pbcore.io import FastaReader, FastaWriter

from LociTools import utils

log = logging.getLogger(__name__)

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

class MissingMetaDataException(ReferenceException):
    pass

class ReferenceIOException(ReferenceException):
    pass


## Private utility functions

def _monthToInt( month ):
    months = {m.lower(): idx for idx, m in enumerate(calendar.month_name)}
    try:
        return months[month.lower()]
    except:
        return -1

def _parseDateStr( date_str ):
    """
    Convert a date string to a numeric tuple for easy ordering
    """
    parts = date_str.strip().split()
    year  = int(parts[0])
    month = month_to_int( parts[1] )
    day   = int(parts[2])
    return (year, month, day)

def _parseVersionStr( version_str ):
    """
    Convert a version string to a numeric tuple for easy ordering
    """
    parts = version_str.strip().split('.')
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])
    return (major, minor, patch)

def _readFasta( filepath ):
    """
    Attempt to read a reference FASTA into memory as a list of records
    """
    try:
        recs = list(FastaReader(filepath))
    except:
        raise ReferenceFormatException('Reference file "{0}" is not a well-formated FASTA file!'.format( filepath ))
    return recs

def _writeFasta( filepath, records ):
    """
    Attempt to write a list of records to a new reference FASTA
    """
    try:
        with FastaWriter( filepath ) as handle:
            for record in records:
                handle.writeRecord( record )
    except:
        raise ReferenceIOException('Unable to write reference FASTA "{0}"'.format( filepath ))

def _writeMap( filepath, data ):
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

def _makeReference( output_path, type_suffix ):
    recs = []
    for resource in pkg.resource_listdir(_REF_DIR, ''):
        if pkg.resource_isdir(_REF_DIR, resource ):
            expected_file = "{0}_{1}.fasta".format(resource, type_suffix)
            expected_path = op.join(_REF_PATH, resource, expected_file)
            if op.exists( expected_path ):
                recs += _read_fasta( expected_path )
            else:
                raise MissingReferenceException('Missing expected reference file "{0}" for Locus "{1}"'.format(expected_file, resource))
    _writeFasta( output_path, recs )
    return True

def _makeExonMap( output_path, locus ):
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
    _writeMap( output_path, data )
    return True

## Public accessor functions

def genomicReferenceExists():
    return utils.isValidFile( _GENOMIC_REF )

def cDNAReferenceExists():
    return utils.isValidFile( _CDNA_REF )

def exonReferenceExists():
    return utils.isValidFile( _EXON_REF )

def makeGenomicReference():
    return _makeReference( _GENOMIC_REF, _GENOMIC_SUFFIX )

def makeCDNAReference():
    return _makeReference( _CDNA_REF, _CDNA_SUFFIX )

def makeExonReference():
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
    _writeMap( _EXON_REF, data )
    return True

def version():
    try:
        with open(_VERSION_REF) as handle:
            return handle.read().strip()
    except:
        raise MissingMetaDataException("Unable to read reference version")

def date():
    try:
        with open(_DATE_REF) as handle:
            return handle.read().strip()
    except:
        raise MissingMetaDataException("Unable to read reference date")

def genomicReference():
    if genomicReferenceExists():
        log.debug("Using existing Genomic Reference FASTA")
        return _GENOMIC_REF
    elif makeGenomicReference():
        log.debug("No Genomic Reference FASTA found, attempting to generate one...")
        return _GENOMIC_REF
    else:
        raise MissingReferenceException('Unable to generate Genomic reference FASTA')

def cDNAReference():
    if cDNAReferenceExists():
        log.debug("Using existing cDNA Reference FASTA")
        return _CDNA_REF
    elif makeCDNAReference():
        log.debug("No cDNA Reference FASTA found, attempting to generate one...")
        return _CDNA_REF
    else:
        raise MissingReferenceException('Unable to generate cDNA reference FASTA')

def exonReference():
    if exonReferenceExists():
        log.debug("Using existing Exon Reference Map")
        return _EXON_REF
    elif makeExonReference():
        log.debug("No Exon Reference Map found, attempting to generate one...")
        return _EXON_REF
    else:
        raise MissingReferenceException('Unable to generate exon reference map')
