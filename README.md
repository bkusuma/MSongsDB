MILLION SONG DATASET
====================

<http://labrosa.ee.columbia.edu/millionsong/>

January 2011
************************************************************

The dataset contains the analysis and metadata for a million songs.
The goal is to provide a large dataset for researchers to report results
on, hence encouraging algorithms that scale to commercial sizes.

Most of the information is provided by The Echo Nest.
The dataset is the result of a collaboration between The Echo Nest
and LabROSA at Columbia University.

Most of the data is licensed the same way as Echo Nest's API.

+ For the SecondHandSongs dataset (cover songs), see the webpage:
  [http://labrosa.ee.columbia.edu/millionsong/secondhand](http://labrosa.ee.columbia.edu/millionsong/secondhand 'SecondHandSongs dataset')

+ For the musiXmatch dataset (lyrics), see the webpage:
  [http://labrosa.ee.columbia.edu/millionsong/musixmatch](http://labrosa.ee.columbia.edu/millionsong/musixmatch 'musiXmatch dataset')

The code is under GNU public license.
See LICENSE for details.

Most details and instructions on how to get the dataset can be found
on the project's website:
<http://labrosa.ee.columbia.edu/projects/millionsong/>

************************************************************
CONTENT
+ Folders A to Z: contain song files in HDF5 format
+ Folder AdditionalFiles: contain SQLite databases, textfiles, etc,
  that helps you navigate through the dataset
  1. unique_tracks.txt: List of all track Echo Nest ID. The format is: `track id<SEP>song id<SEP>artist name<SEP>song title`
  2. unique_artists.txt: List of all artist ID. The format is: `artist id<SEP>artist mbid<SEP>track id<SEP>artist name`
      + The code to recreate that file is available at `Tasks_Demos/NamesAnalysis/list_all_artists.py` (and a faster version using the SQLite databases is at `Tasks_Demos/SQLite/list_all_artists_from_db.py`).
  3. unique_terms.txt: List of all unique artist terms (Echo Nest tags).
  4. unique_mbtags.txt: List of all unique artist musicbrainz tags.
  5. tracks_per_year.txt: List of the 515,576 tracks for which we have the year information, ordered by year.
  6. artist_location.txt: List of artists for which we know latitude and longitude.
  7. msd_summary_file.h5: Summary file of the whole dataset, meaning same HDF5 format as regular files, it contains all metadata but no arrays like audio analysis, similar artists and tags. Only 300 Mb.
  8. track_metadata.db: SQLite database containing most metadata about each track (NEW VERSION 03/27/2011).
  9. artist_term.db: SQLite database linking artist ID to the tags (Echo Nest and musicbrainz ones).
  10. artist_similarity.db: SQLite database containing similarity among artists.
+ millionsongsubset.tar.gz contains a copy of 10K 'random' songs
  (mostly well-known artists) from the dataset
+ License file and Readme file

************************************************************

If you have any question or comment:
Thierry Bertin-Mahieux
<tb2332@columbia.edu>

If you have any questions or comments:
<https://groups.google.com/forum/#!forum/millionsongdataset>
