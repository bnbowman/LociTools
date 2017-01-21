
from collections import namedtuple

from pbcore.io.base import ReaderBase, WriterBase, getFileHandle

blasrM1Spec = 'qname tname qstrand tstrand score pctsimilarity tstart tend tlength qstart qend qlength ncells'
blasrM5Spec = 'qname qlength qstart qend qstrand tname tlength tstart tend tstrand score nmat nmis nins ndel ' + \
                'mapqv qstring astring tstring'
BlasrM1 = namedtuple('BlasrM1', blasrM1Spec)
BlasrM5 = namedtuple('BlasrM5', blasrM5Spec)


class BlasrTypeError(TypeError):
    pass


class BlasrReader( ReaderBase ):

    def __init__(self, f, filetype=None):
        print f, filetype
        self.file = getFileHandle(f, 'r')

        filetype = filetype or f.split('.')[-1]
        if filetype.lower() == 'm1':
            self._filetype = 'm1'
            self._datatype = BlasrM1
        elif filetype.lower() == 'm5':
            self._filetype = 'm5'
            self._datatype = BlasrM5
        else:
            raise BlasrTypeError("Invalid type to BlasrReader")

    @property
    def filetype(self):
        return self._filetype

    def __iter__(self):
        try:
            for line in self.file:
                entry = self._datatype._make(line.strip().split())
                if entry.qname == 'qname':
                    continue
                yield entry
        except:
            raise ValueError("Invalid Blasr entry of type %s" % self.filetype)


class BlasrWriter( WriterBase ):
    """
    A Class for writing out Blasr records
    """

    def _writeHeader( self, filetype ):
        if filetype == 'm1':
            self.file.write( blasrM1Spec )
        elif filetype == 'm5':
            self.file.write( blasrM5Spec )
        else:
            raise ValueError("Filetype must be M1 or M5!")
        self.file.write("\n")

    def _recordToString( self, record ):
        if isinstance(record, BlasrM1):
            return "%s %s %s %s %s %s %s %s %s %s %s %s %s" % (record.qname,
                    record.tname, record.qstrand, record.tstrand, record.score,
                    record.pctsimilarity, record.tstart, record.tend,
                    record.tlength, record.qstart, record.qend, record.qlength,
                    record.ncells)
        elif isinstance(record, BlasrM5):
            return "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s" % (
                    record.qname, record.qlength, record.qstart, record.qend,
                    record.qstrand, record.tname, record.tlength, record.tstart,
                    record.tend, record.tstrand, record.score, record.nmat,
                    record.nmis, record.nins, record.ndel, record.mapqv,
                    record.qstring, record.astring, record.tstring)
        else:
            raise BlasrTypeError("Invalid type to BlasrReader")

    def writeRecord( self, record ):
        """
        Write a Blasr record out to the file handle
        """
        if isinstance( record, BlasrM1 ) or isinstance( record, BlasrM5 ):
            self.file.write( self._recordToString( record ) + "\n" )
            self.file.write("\n")
        else:
            raise BlasrTypeError("Invalid type to BlasrReader")

    def write( self, records ):
        """
        Write all Blasr records in a container out to the file handle
        """
        for record in records:
            self.writeRecord( record )
