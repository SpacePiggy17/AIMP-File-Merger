# Problem
Want to merge files from an exported AIMP database together. AIMP doesn't seem to do the best job of detecting name changes so we have to manually merge a deleted file's stats with an existing file's stats.

# Implementation
The program first creates a copy of `MusicLibrary.db` as `MusicLibrary_new.db`, which is updated later.
Then we get the rows in the "Tracks" table of the database and compare each deleted track to the existing tracks.
If the titles are similar, we then prompt the user to merge the deleted track's play count into the existing track.
The track names, play counts, and duration are listed in order to help the user make an informed decision on whether to merge the tracks.
If track `a` is merged into track `b`, track `b`'s play count is updated and track `a` is scheduled for deletion.
Finally, the "Tracks" table in `MusicLibrary_new.db` is replaced with the new rows.

# Usage
Clone the repo and run `python merger.py path/to/MusicLibrary.db`.
The program will prompt the user for each pair of similar files.
The updated file is written to `MusicLibrary_new.db`.
To use the updated file, the user replaces the old `MusicLibrary.db` with the `MusicLibrary_new.db` file and zips the entire AIMP settings folder.
Then the settings zip can be imported into AIMP. **Currently AIMP says this file is invalid.**
