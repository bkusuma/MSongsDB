# python list_all_artists_from_db.py "C:\Users\foste\Desktop\Projects\delistyle\data\full\track_metadata.db" "C:\Users\foste\Desktop\Projects\delistyle\data\reference_lists\artistlist.txt"

"""
Thierry Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu

This code creates a text file with all artist ids,
same as /Tasks_Demos/Name_Analysis
but faster since we use the sqlite database: track_metadata.db
Of course, it takes time to create the dataset ;)

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
list_all_artists_from_db.py
  by T. Bertin-Mahieux (2010) Columbia University

Mimics the program /Tasks_Demo/NamesAnalysis/list_all_artist.py
but assumes the sqlite db track_metadata.db is available
i.e. it takes a few seconds instead of a few hours!

To download track_metadata.db, see Million Song website.
To recreate it, see create_track_metadata_db.py.

Usage:
  python list_all_artists_from_db.py track_metadata.db output.txt
  Creates a file where each line is: (one line per artist)
  artist id<SEP>artist mbid<SEP>track id<SEP>artist name""")
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
    c = conn.cursor()
    # get what we want
    q = 'SELECT artist_id,artist_mbid,track_id,artist_name FROM songs'
    q += ' GROUP BY artist_id  ORDER BY artist_id'
    res = c.execute(q)
    alldata = res.fetchall()
    # DEBUGGING
    q = 'SELECT DISTINCT artist_id FROM songs'
    res = c.execute(q)
    artists = res.fetchall()
    print('Found', len(artists), 'distinct artists.')
    assert len(alldata) == len(artists), 'incoherent sizes'
    # close db connection
    c.close()
    conn.close()

    # write to file
    with open(output, 'w', encoding='utf-8') as f:
        for artist_id, artist_mbid, track_id, artist_name in alldata:
            # Ensure all parts are strings before joining, especially if some could be None
            f.write(str(artist_id) + '<SEP>' + str(artist_mbid) + '<SEP>' + str(track_id) + '<SEP>')
            f.write(str(artist_name) + '\n')

    # done
    t2 = time.time()
    stimelength = str(datetime.timedelta(seconds=t2-t1))
    print('File', output, 'with', len(alldata), 'artists created in', stimelength)
