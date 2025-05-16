"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

Code to quickly see the content of an HDF5 file.

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
import hdf5_getters
import numpy as np


def die_with_usage():
    """ HELP MENU """
    print('display_song.py')
    print('T. Bertin-Mahieux (2010) tb2332@columbia.edu')
    print('To quickly display all we know about a song.')
    print('\nUsage:')
    print('  python display_song.py [FLAGS] <HDF5 file> [song_idx] [getter]')
    print('\nExample:')
    print('  python display_song.py mysong.h5 0 danceability')
    print('\nINPUTS:')
    print('  <HDF5 file>  - Any song / aggregate / summary file.')
    print('  [song_idx]   - If file contains many songs, specify one (starting at 0). Optional.')
    print('  [getter]     - If you want only one field, you can specify it')
    print('                 e.g. "get_artist_name" or "artist_name". Optional.')
    print('\nFLAGS:')
    print('  -summary     - If you use a file that does not have all fields,')
    print('                 use this flag. If not, you might get an error!')
    print('                 Specifically designed to display summary files.')
    sys.exit(0)


if __name__ == '__main__':
    """ MAIN """

    # help menu
    if len(sys.argv) < 2:
        die_with_usage()

    # flags
    summary = False
    while True:
        if sys.argv[1] == '-summary':
            summary = True
        else:
            break
        sys.argv.pop(1)

    # get params
    hdf5path = sys.argv[1]
    songidx = 0
    if len(sys.argv) > 2:
        songidx = int(sys.argv[2])
    onegetter = ''
    if len(sys.argv) > 3:
        onegetter = sys.argv[3]

    # sanity check
    if not os.path.isfile(hdf5path):
        print('ERROR: file', hdf5path, 'does not exist.')
        sys.exit(0)
    h5 = hdf5_getters.open_h5_file_read(hdf5path)
    numSongs = hdf5_getters.get_num_songs(h5)
    if songidx >= numSongs:
        print('ERROR: file contains only', numSongs, 'songs.')
        h5.close()
        sys.exit(0)

    # get all getters
    getters_list = [f_name for f_name in dir(hdf5_getters) if f_name.startswith('get_')]
    if "get_num_songs" in getters_list:
        getters_list.remove("get_num_songs") # special case
    if onegetter == 'num_songs' or onegetter == 'get_num_songs':
        getters_list = []
    elif onegetter != '':
        if onegetter[:4] != 'get_':
            onegetter = 'get_' + onegetter
        try:
            getters_list.index(onegetter) # Check if valid getter
        except ValueError:
            print('ERROR: getter requested:', onegetter, 'does not exist.')
            h5.close()
            sys.exit(0)
        getters_list = [onegetter]
    getters_list = np.sort(getters_list)

    # print them
    for getter in getters_list:
        try:
            res = hdf5_getters.__getattribute__(getter)(h5,songidx)
        except AttributeError as e:
            if summary:
                continue
            else:
                print(e)
                print('Forgot -summary flag? Specified wrong getter?')
        if res.__class__.__name__ == 'ndarray':
            print(getter[4:] + ": shape =", res.shape)
        else:
            print(getter[4:] + ":", res)

    # done
    print('DONE, showed song', songidx, '/', numSongs - 1, 'in file:', hdf5path)
    h5.close()
    
