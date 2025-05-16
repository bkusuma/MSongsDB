"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates a text file with all track ID, song ID, artist name and
song name. Does it from the track_metadata.db
format is:
trackID<SEP>songID<SEP>artist name<SEP>song title

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

import datetime
import glob
import os
import sys
import sqlite3
import string
import time

try:
    import numpy as np
except ImportError:
    print('You need numpy installed to use this program.')
    print('Run `pip install numpy` and try again.')
    sys.exit(0)


def die_with_usage():
    print("""
HELP MENU
list_all_tracks_from_db.py
  by T. Bertin-Mahieux (2010) Columbia University

Code to create a list of all tracks in the dataset as
a text file. Assumes track_metadata.db already exists.
Format is (IDs are EchoNest's):
  trackID<SEP>songID<SEP>artist name<SEP>song title

Usage:
  python list_all_tracks_from_db.py <track_metadata.db> <output.txt>""")
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 3:
        die_with_usage()

    # params
    dbfile = sys.argv[1]
    output = sys.argv[2]

    # sanity check
    if not os.path.isfile(dbfile):
        print('ERROR: Cannot find database:', dbfile)
        sys.exit(0)
    if os.path.exists(output):
        print('ERROR: File', output, 'exists, delete or provide a new name.')
        sys.exit(0)

    # start time
    t1 = time.time()

    # connect to the db
    conn = sqlite3.connect(dbfile)

    # get what we want
    q = 'SELECT track_id,song_id,artist_name,title FROM songs'
    res = conn.execute(q)
    alldata = res.fetchall() # takes time and memory!
    
    # close connection to db
    conn.close()

    # sanity check
    if len(alldata) != 1000000:
        print(f'WARNING: Expected 1,000,000 tracks, but found {len(alldata)}.')

    # write to file
    with open(output, 'w', encoding='utf-8') as f:
        for track_id, song_id, artist_name, title in alldata:
            # Ensure all parts are strings
            f.write(str(track_id) + '<SEP>' + str(song_id) + '<SEP>')
            f.write(str(artist_name) + '<SEP>')
            f.write(str(title) + '\n')

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print('File', output, 'created in', stimelength)
