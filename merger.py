import sys
import sqlite3
import shutil # Copying files
import os
import difflib # Comparing differences between two strings
import re # Regular expressions
import math # For is close

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[31m"

'''
Open the database file and create a backup
'''
# Path to the SQLite database files
if len(sys.argv) < 2:
    print("Usage: python editor.py <path/to/MusicLibaray.db>")
    exit(1)
source_file_path = sys.argv[1]

# Check if the source file path ends with "MusicLibrary.db"
if not source_file_path.endswith("MusicLibrary.db"):
    print(f"Source file {source_file_path} does not end with 'MusicLibrary.db'.")
    print("Usage: python editor.py <path/to/MusicLibaray.db>")
    exit(1)

new_file_path = source_file_path.replace(".db", "_new.db")

# Create a backup of the original database file
if os.path.exists(source_file_path):
    shutil.copy(source_file_path, new_file_path)
else:
    print(f"Source file {source_file_path} does not exist.")
    exit(1)

# Connect to the SQLite database and create a cursor to interact with it
connection = sqlite3.connect(source_file_path)
cursor = connection.cursor()

# Execute a query to retrieve all rows from the "Tracks" table
cursor.execute("SELECT * FROM Tracks")
rows = cursor.fetchall()

# Close the cursor and connection
cursor.close()
connection.close()

'''
Process the rows

Rows follow this format:
     0. File path
     1. Part ID
     2. Missing
     3. Filename
     4. File duration
     5. File size (in bytes)
     6. Disk number
     7. Track number
     8. Album ID
     9. Album artist ID
    10. Artist ID
    11. Genre ID
    12. Title
    13. Year
    14. Date added
    15. Date modified
    16. Date played
    17. ReplayGain album
    18. ReplayGain track
    19. Duration
    20. Size (bytes)
    21. Play count
    22. Bitrate
    23. Channels
    24. Sample rate
    25. Rating
'''
def get_duration_color(duration1, duration2):
    """
    Compare two durations and return a color based on their similarity.
    """
    if math.isclose(duration1, duration2, rel_tol=1e-):
        return GREEN
    elif math.isclose(duration1, duration2, rel_tol=1e-2):
        return YELLOW
    else:
        return RED


to_remove_indices = []
for i, row in enumerate(rows):
    # If file is missing, check for similar file(s) to update
    if row[2] == 1: # If file is missing
        if row[21] == 0: # If play count is 0, add it to the list of files to remove
            to_remove_indices.append(i)
            continue
        
        title = row[12]

        # Remove ".trashed-any number-" from the file name
        title = re.sub(r'\.trashed-\d+-', '', title)

        for j, other_row in enumerate(rows):
            if other_row[2] == 0: # If other file is not missing
                # Compare the titles of the missing file and the other file
                if difflib.SequenceMatcher(None, title, other_row[12]).ratio() > 0.95:
                    # If they are similar, ask to update
                    path1, path2 = row[0], other_row[0]
                    # Remove "local::/primary" from the file paths
                    path1 = path1.replace("local://primary", "")
                    path2 = path2.replace("local://primary", "")

                    duration_color = get_duration_color(row[4], other_row[4])
                    print(f"a. {path1} : {CYAN}{row[21]}{RESET}, {duration_color}{row[4]}{RESET}\nb. {path2} : {CYAN}{other_row[21]}{RESET}, {duration_color}{other_row[4]}{RESET}")

                    response = "z"
                    while response != "y" and response != "n" and response != "":
                        response = input("Merge a into b? (y/n): ").strip().lower()

                    print()

                    if response == "y": # Merge row into other_row
                        # Add the missing file's play count to the other file
                        updated_row = (other_row[0], other_row[1], other_row[2], other_row[3], other_row[4], other_row[5],
                                     other_row[6], other_row[7], other_row[8], other_row[9], other_row[10],
                                     other_row[11], other_row[12], other_row[13], other_row[14], other_row[15],
                                     other_row[16], other_row[17], other_row[18], other_row[19], other_row[20],
                                     other_row[21] + row[21], # Update play count
                                     other_row[22], other_row[23], other_row[24], other_row[25])
                        
                        rows[j] = updated_row # Replace the other_row with the updated_row (update play count)
                        
                        to_remove_indices.append(i) # Mark the missing file for removal

# Remove duplicates from the list of indices to remove
to_remove_indices = list(set(to_remove_indices))

# Remove the marked rows from the list
for index in sorted(to_remove_indices, reverse=True):
    del rows[index]

'''
Update the database with the new rows
'''
# Connect to the new SQLite database file and create a cursor to interact with it
connection = sqlite3.connect(new_file_path)
cursor = connection.cursor()

# Replace the existing "Tracks" table with the new rows
cursor.execute("DROP TABLE IF EXISTS Tracks") # Delete the old table

# Create a new "Tracks" table with the same schema as the original
cursor.execute("CREATE TABLE 'tracks' (`uri` TEXT NOT NULL, `partId` INTEGER NOT NULL, `missing` INTEGER NOT NULL, `file_name` TEXT, `file_duration` REAL NOT NULL, `file_size` INTEGER NOT NULL, `disk_no` INTEGER NOT NULL, `track_no` INTEGER NOT NULL, `album_id` INTEGER NOT NULL, `album_artist_id` INTEGER NOT NULL, `artist_id` INTEGER NOT NULL, `genre_id` INTEGER NOT NULL, `title` TEXT, `year` TEXT, `date_added` INTEGER NOT NULL, `date_modified` INTEGER NOT NULL, `date_played` INTEGER NOT NULL, `replaygain_album` REAL NOT NULL, `replaygain_track` REAL NOT NULL, `duration` REAL NOT NULL, `size` INTEGER NOT NULL, `playcount` INTEGER NOT NULL, `bitrate` INTEGER NOT NULL, `channels` INTEGER NOT NULL, `sampleRate` INTEGER NOT NULL, `rating` INTEGER NOT NULL, PRIMARY KEY(`uri`, `partId`))")

# Insert the new rows into the "Tracks" table
cursor.executemany("INSERT INTO 'tracks' VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
connection.commit()

'''
Clean up
'''
# Close the cursor and connection
cursor.close()
connection.close()
print("Database connection closed.")
