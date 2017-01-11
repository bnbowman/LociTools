
import logging
import subprocess
import os.path as op

from LociTools import utils

log = logging.getLogger(__name__)


class BlasrExecutableError(Exception):
    pass

class BlasrIOError(IOError):
    pass

class BlasrRunner( object ):

    _validFiles = []
    _refWithIndex = []
    _refSizes = {}

    def __init__( self, exe=None, nproc=8 ):
        if exe is None:
            log.debug("No BLASR executable supplied, searching PATH...")
            self._exe = utils.which('blasr')
        elif utils.isExe( exe ):
            log.debug("Using supplied BLASR executable at {0}".format(exe))
            self._exe = op.abspath( exe )
        else:
            raise BlasrExecutableError("No blasr executable supplied or in PATH!")
        self._nproc = nproc

    def _validateQuery( self, query ):
        if query not in self._validFiles:
            if utils.isValidFile( query ):
                self._validFiles.append( query )
            else:
                msg = "Supplied query file for BLASR isn't valid"
                log.error( msg )
                raise BlasrIOError( msg )

    def _validateReference( self, refFile ):
        print refFile
        if refFile not in self._validFiles:
            print refFile
            if utils.isValidFasta( refFile ):
                print refFile
                self._validFiles.append( refFile )
            else:
                print refFile
                msg = "Supplied reference FASTA for BLASR isn't valid"
                log.error( msg )
                raise BlasrIOError( msg )

    def _validateArgs( self, args ):
        if "out" not in args.keys():
            msg = "No valid output file for BLASR supplied!"
            log.error( msg )
            raise BlasrIOError( msg )
        elif utils.isValidFile( args["out"] ):
            utils.removeFile( args["out"] )

    def _validateOutput( self, outFile ):
        if utils.isValidFile( outFile ):
            return outFile
        else:
            msg = 'An unknown error occurred - output file "{0}" isn''t valid'.format(outFile)
            log.error( msg )
            raise BlasrIOError( msg )

    def _formatCommand( self, query, reference, args ):
        """Format a dictionary of arguments into a callable list"""
        command = [self._exe, query, reference]
        for arg, value in args.iteritems():
            if len(arg) == 1:
                arg = '-' + str(arg)
            else:
                arg = '--' + str(arg)
            if value is True:
                command += [arg]
            else:
                command += [arg, str(value)]
        # Add in the index, if available
        if "sa" not in args:
            saFile = reference + ".sa"
            if reference in self._refWithIndex:
                command += ["--sa", saFile]
            elif utils.isValidFile( saFile ):
                command += ["--sa", saFile]
        return command

    def _logCommand( self, cmd ):
        """Log the command for debugging purposes"""
        cmd = list( cmd )
        command = cmd.pop(0)
        cmdString = " ".join(cmd)
        log.debug('Calling BLASR with the following options: {0}'.format(cmdString))

    def _executeCommand( self, command ):
        log.debug('Executing BLASR command as subprocess' % command)
        with open('/dev/null', 'w') as handle:
            subprocess.check_call( command,
                                   stdout=handle,
                                   stderr=subprocess.STDOUT )
        log.debug("Subprocess finished successfully")

    def __call__( self, query, refFile, args ):
        """
        Call Blasr
        """
        self._validateQuery( query )
        self._validateReference( refFile )
        self._validateArgs( args )
        cmd = self._formatCommand( query, refFile, args )
        self._logCommand( cmd )
        self._executeCommand( cmd )
        self._validateOutput( args["out"] )

        # Return the output file for parsing
        return args["out"]

    def fullBestAlignment( self, query, refFile, output=None ):
        if output is None:
            output = "temp.m5"
        self._validateReference( refFile )
        refCount = utils.fastaRecordCount( refFile )
        args = {'nproc': self._nproc,
                'out': output,
                'm': 5,
                'bestn': 1,
                'nCandidates': refCount,
                'noSplitSubreads': True}
        return self(query, refFile, args)
