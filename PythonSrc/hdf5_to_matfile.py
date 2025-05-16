"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu


This code transforms a HDF5 file to a matlab file, with
the same information (as much as possible!)

This is part of the Million Song Dataset project from
LabROSA (Columbia University) and The Echo Nest.


Copyright 2010, Thierry Bertin-Mahieux

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import time
import glob
try:
    import scipy.io as sio
    import numpy as np
except ImportError:
    print('ERROR: You need SciPy and NumPy to create .mat files!')
    print('Both are freely available at: http://www.scipy.org/')
    sys.exit(1) # Or raise the original error if preferred
# project code
import hdf5_getters
import utils


def transfer(h5path,matpath=None,force=False):
    """
    Transfer an HDF5 song file (.h5) to a matfile (.mat)
    If there are more than one song in the HDF5 file, each
    field name gets a number happened: 1, 2, 3, ...., numfiles
    PARAM
        h5path  - path to the HDF5 song file
        matpath - path to the new matfile, same as HDF5 path
                  with a different extension by default
        force   - if True and matfile exists, overwrite
    RETURN
        True if the file was transfered, False if there was
        a problem.
        Could also raise an IOException
    NOTE
        All the data has to be loaded in memory! be careful
        if one file contains tons of songs!
    """
    # sanity checks
    if not os.path.isfile(h5path):
        print('Path to HDF5 file does not exist:', h5path)
        return False
    if not os.path.splitext(h5path)[1] == '.h5':
        print('Expecting a .h5 extension for file:', h5path)
        return False
    # check matfile
    if matpath is None:
        matpath = os.path.splitext(h5path)[0] + '.mat'
    if os.path.exists(matpath):
        if force:
            print('Overwriting file:', matpath)
        else:
            print('Matfile', matpath, 'already exists (delete or use --force).')
            return False
    # get all getters! we assume that all we need is in hdf5_getters.py
    # further assume that they have the form get_blablabla and that's the
    # only thing that has that form
    getters_list = [f_name for f_name in dir(hdf5_getters) if f_name.startswith('get_')]
    if "get_num_songs" in getters_list:
        getters_list.remove("get_num_songs") # special case
    # open h5 file
    h5 = hdf5_getters.open_h5_file_read(h5path)
    # transfer
    nSongs = hdf5_getters.get_num_songs(h5)
    matdata = {'transfer_note':'transferred on '+time.ctime()+' from file: '+h5path}
    try:
        # iterate over songs
        for songidx in range(nSongs):
            # iterate over getter
            for getter in getters_list:
                gettername = getter[4:]
                if nSongs > 1:
                    gettername += str(songidx+1)
                data = hdf5_getters.__getattribute__(getter)(h5,songidx)
                matdata[gettername] = data
    except MemoryError:
        print('Memory Error with file:', h5path)
        print('All data has to be loaded in memory before being saved as a .mat file.')
        print('Is this an aggregated / summary file with many songs?')
        print('This code is optimized for files containing one song.')
        print('Contact the author for assistance with large files. (TBM)')
        raise
    finally:
        # close h5
        h5.close()
    # create
    sio.savemat(matpath,matdata)
    # all good
    return True



def die_with_usage():
    """ HELP MENU """
    print('hdf5_to_matfile.py')
    print('Transforms a song file in HDF5 format to a .mat file')
    print('with the same information.')
    print('')
    print('Usage:')
    print('  python hdf5_to_matfile.py <DIR_OR_FILE_PATH>')
    print('\nPARAMS:')
    print('  <DIR_OR_FILE_PATH>   - If a file (e.g., TR123.h5), creates TR123.mat in the same directory.')
    print('                         - If a directory, processes all .h5 files in every subdirectory.')
    print('')
    print('REQUIREMENTS:')
    print('  HDF5 C library, NumPy, SciPy, PyTables')
    print('')
    print('NOTE:')
    print('  The main function is "transfer", which you can use in your scripts.')
    print('  For instance, if you have a subset of songs of interest, pass each song path to "transfer".')
    print('  Data for each song is loaded into memory, which can be resource-intensive for')
    print('  aggregated / summary HDF5 files containing many songs.')
    print('')
    print('Copyright: T. Bertin-Mahieux (2010) Columbia University')
    print('tb2332@columbia.edu')
    print('Million Song Dataset project with LabROSA and The Echo Nest')
    sys.exit(0)

if __name__ == '__main__':

    # HELP MENU
    if len(sys.argv) < 2:
        die_with_usage()

    # GET DIR/FILE
    if not os.path.exists(sys.argv[1]):
        print('File or directory:', sys.argv[1], 'does not exist.')
        sys.exit(0)
    if os.path.isfile(sys.argv[1]):
        if os.path.splitext(sys.argv[1])[1] != '.h5':
            print('We expect a .h5 extension for file:', sys.argv[1])
            sys.exit(0)
        allh5files = [ os.path.abspath(sys.argv[1]) ]
    elif not os.path.isdir(sys.argv[1]):
        print(sys.argv[1], "is neither a file nor a directory. Confused... a link?")
        sys.exit(0)
    else:
        allh5files = utils.get_all_files(sys.argv[1],ext='.h5')
    if len(allh5files) == 0:
        print('No .h5 files found. Please check the directory:', sys.argv[1])

    # final sanity checks
    for f in allh5files:
        assert os.path.splitext(f)[1] == '.h5','file with wrong extension? should have been caught earlier... file='+f
    nFiles = len(allh5files)
    if nFiles > 1000:
        print('You are creating', nFiles, 'new MATLAB files. Hope you have the space and time!')

    # let's go!
    cnt = 0
    for f in allh5files:
        filedone = transfer(f)
        if filedone:
            cnt += 1

    # summary report
    print('Processed', cnt, 'files out of', len(allh5files))
    if cnt == len(allh5files):
        print('Congratulations!')
    

    
