# METAparser
python3 to parse META search warrant return chats into categorized, searchable csv files

If you don't know anything about python, use the Executable. Otherwise, only dependency if you are using Python is Python3, no other libraries.

USE:
This script works for Facebook and Instagram search warrant returns, which were changed in 2024 to a new format that no longer comes with a PDF.


1. Unzip your warrant return data
2.  Drag and drop the 'records.html' file onto this script or .exe
    - For some reason windows doesn't like this all the time. So you can just run the script in the same folder as your return
3. Be patient...
4. In the directory you have the records.html file, you will now have several .csv files. One being '_threadList.csv' which should be the main navigation to each individual thread, and several other .csv files that have a single thread only.
5. Once complete, I would recommend navigating using the _threadList.csv file, as it will contain hyperlinks to the chats. I typically convert _threadList.csv to xlsx after I format it, but the actual thread files should stay as .csv files, otherwise it will break the links.

Of notice should be that the .csv is not separated by normal commas as a comma in chat will break the .csv. Instead, they are separated by a 'pipe' | (located above the enter key on your keyboard). I highly recommend that you change your region settings to get this working properly. To do this:

1. Hit the start button and type “region”. Chose the first option.
2. In the new pop up, choose “Additional Settings”
3. Change the option “List Separator” from a comma to the pipe |, then hit okay

Known Issues:
    -Currently its only doing Messages and not "shares" or other "group" enabled options. As I deal with more warrant return data, I'll be able to implement that in.
    -I need more datasets to start implenting other features, such as IP address queries, etc.
