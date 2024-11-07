#!Python3
# Created by Thomas 'Lily' Lilienthal OCT.2024 - Deschutes County, Oregon - v1
'''
This script works for Facebook and Instagram search warrant returns, which
were changed in 2024 to a new format that no longer comes with a PDF.

1) Unzip your warrant return data
2) Drag and drop the 'records.html' file onto this script or .exe
    -For some reason windows doesn't like this all the time. 
        So you can just run the script in the same folder as your return
3) Be patient...
4) In the directory you have the records.html file, you will now have 
    several .csv files. One being '_threadList.csv' which should be the main
    navigation to each individual thread, and several other .csv
    files that have a single thread only.

Of notice should be that the .csv is not separated by normal commas
as a comma in chat will break the .csv. Instead, they are separated by
a 'pipe' | (located above the enter key on your keyboard)

Known Issues:
    -Currently its only doing Messages and not "shares" or other "group" enabled options.
        As I deal with more warrant return data, I'll be able to implement that in.
'''

import sys
import os
import re
import csv

def extractSectionToText(htmlFilePath, outputTextFilePath, keywords):
    # Open the HTML file for reading
    with open(htmlFilePath, 'r', encoding='utf-8') as htmlFile:
        # Open the output text file for writing
        with open(outputTextFilePath, 'w', encoding='utf-8') as textFile:
            insideSection = False  # Flag to track when we're within the target section

            # Read the HTML file line by line
            for line in htmlFile:
                # Check for the start boundary
                if '<div class="t o"><div class="t i">Unified Messages<div class="m"><div>' in line: insideSection = True

                # Stop processing and break if we hit the stopping boundary
                if '<div class="mvm uiP fsm">' in line: break

                # If we're within the boundaries, process the line
                if insideSection:
                    # Remove 'Meta Platforms Business Record Page X' but keep the rest of the line
                    cleanLine = re.sub(r'Meta Platforms Business Record Page \d{1,6}', '', line)
                    
                    # Remove everything between < and > including those characters
                    cleanLine = re.sub(r'<[^>]*>', '', cleanLine).strip()
                    
                    # Skip blank lines
                    if not cleanLine: continue

                    # Add colon and space if the line starts with certain keywords
                    for keyword in keywords:
                        if cleanLine.startswith(keyword):
                            cleanLine = f"{keyword}: {cleanLine[len(keyword):].strip()}"
                            break

                    # Write the cleaned line to the output text file
                    textFile.write(cleanLine + '\n')

                # Check for the end boundary and stop writing
                if '<div id="property-reported_conversations" class="content-pane">' in line:insideSection = False

    print(f"Data extracted and <div> elements cleaned to {outputTextFilePath}.")

def strippedDataCleanup(inputTextFilePath):
    # This is messy and I can probably streamline it later, but its basically cleaning up all the issues
    # From eliminating the <div> elements, including the false \n values because of broken key:value entries
    # ****The downside to this is to include anything else that may not be explicitly identified, we have to hardcode it
    message = {} # Dictionary helps to establish the key:value relationships for writing from the split lines
    linesToWrite = [] # Everything that we are keeping is placed into a list then written at the end
    lastKey = '' # Works as a marker to track if the key:value is split by \n from the broken <div> elements
    
    # Opens the parsed text read only
    with open(inputTextFilePath, 'r', encoding='utf-8') as inFile:

        # Read line-by-line to keep specific data, combine key:value on same line, and add it all to linesToWrite
        # Each if/elif is pretty much the same:
        '''
        If the key is found in the line: check if the value is in the same line. If it is, cool, write it
        Else: keep track of what the key is so the next loop will combine the key:value to write
        '''
        for line in inFile.readlines():
            if lastKey != '': # Will enter this if we are dealing with a split key:value
                message[lastKey] = line.strip()
                lastKey = ''
            if line.startswith('Thread'): 
                value = line.strip().split('Thread ')
                if len(value) > 1: 
                    message['Thread '] = value[1]
                    lastKey = ''
                else: lastKey = 'Thread '
            elif line.startswith('Current Participants: '): 
                # Removes the date/time from Current Participants, as this is always the time that META did the data production
                line = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} UTC', '', line).strip()
                value = line.strip().split('Current Participants: ')
                if len(value) > 1: 
                    message['Current Participants: '] = value[1]
                    lastKey = ''
                else: lastKey = 'Current Participants: '
            elif line.startswith('Author:'):
                # We write and reset the dictionary here to avoid overwriting every single message
                for k,v in message.items(): linesToWrite.append(f'''{k}{v}''')
                message = {}
                value = line.strip().split('Author: ')
                if len(value) > 1: 
                    message['Author: '] = value[1]
                    lastKey = ''
                else: lastKey = 'Author: '
            elif line.startswith('Sent:'):
                value = line.strip().split('Sent: ')
                if len(value) > 1: 
                    message['Sent: '] = value[1]
                    lastKey = ''
                else: lastKey = 'Sent: '
            elif line.startswith('Body:'):
                value = line.strip().split('Body: ')
                if len(value) > 1: 
                    message['Body: '] = value[1]
                    lastKey = ''
                else: lastKey = 'Body: '
            elif line.startswith('Linked Media File:'):
                # This handles having multiple shared files in a single message
                value = line.strip().split('Linked Media File:')
                if 'Linked Media File: ' in message.keys(): message['Linked Media File: '] += f',{value[1]}'
                else: message['Linked Media File: '] = value[1]
                lastKey = ''
        for k,v in message.items(): linesToWrite.append(f'''{k}{v}''') #just handles the final write

    # Now that everything is further parsed in linesToWrite, we write it all to our parsed file
    with open(inputTextFilePath, 'w', encoding='utf-8') as outFile:
        for line in linesToWrite: 
            outFile.write(f'{line}\n')


    print('Data further parsed down and pared to key:value pairs. Creating docs...')

def dataToThreadList(inputTextFilePath):
    # Creates the threadindex and all the individual threads as CSV '|' delimited
    dataToFile = []
    threadFile = ''
    # Open the stripped text file for reading and CSV for writing
    with open(inputTextFilePath, 'r', encoding='utf-8') as inFile:
        with open(f'''{'\\'.join(inputTextFilePath.split('\\')[0:-1])}\\_threadList.csv''', 'w', newline='', encoding='utf-8') as indexFile:
            print('_threadList.csv Created.')
            indexWriter = csv.writer(indexFile, delimiter='|')

            # Write CSV headers
            indexWriter.writerow(['Thread ID', 'Participants', 'Link to Chat'])

            # List to handle writing links for individual threads
            indexToFile = []
            dataToFile = []
            # Start Parsing. First Parses the _threadList.csv entry, then parses the chat itself
            for line in inFile.readlines():
                if line.startswith('Thread'): # Identifier that a new chat thread is starting
                    # This is a catch for the last message of the previous thread. Without this catch, the last message of the previous thread
                    # Will become the first message of the next thread.
                    if dataToFile != []: 
                        threadWriter.writerow(dataToFile)
                        dataToFile = []
                    # Use regex to find the thread number within parentheses, create the chat thread csv
                    match = re.search(r'\((\d+)\)', line)
                    if match:
                        # Handles closing an open thread file if a new thread is identified
                        if type(threadFile) is not str and threadFile.closed == False: 
                            threadFile.close() 
                            print(f'---All data added to thread_{threadID}.csv. Moving to next file.')
                        threadID = match.group(1) 
                        indexToFile.append(f'"{threadID}"')
                        currentThread = f'''{'\\'.join(inputTextFilePath.split('\\')[0:-1])}\\thread_{threadID}.csv'''
                        print(f'thread_{threadID}.csv created.')
                        threadFile = open(currentThread, 'w', newline='', encoding='utf-8')
                        threadWriter = csv.writer(threadFile, delimiter='|')
                        threadWriter.writerow(['Author','Datetime Sent','Body','Attachments']) # Header for thread csv
                elif line.startswith('Current Participants'):
                    # Writes link and thread info to the index
                    indexToFile.append(line.split('Current Participants: ')[-1].strip('\n'))
                    indexToFile.append(f'''=HYPERLINK("{currentThread.split('\\')[-1]}")''')
                    indexWriter.writerow(indexToFile)
                    indexToFile = []
                else: # Inside the thread, parse the chats
                    if line.startswith('Author') and dataToFile != []: # First check if a message is ready to be written
                        threadWriter.writerow(dataToFile)
                        dataToFile = []
                    # These can be infinately expanded here as there are small use case datasets. However for now
                    # Just getting it to parse the meat and potatoes, author,sent,body,linkedmedia
                    if line.startswith('Author:'): dataToFile.append(line.split('Author: ')[1].strip('\n'))
                    elif line.startswith('Sent:'): dataToFile.append(line.split(': ')[1].strip('\n'))
                    elif line.startswith('Body:') and len(line.split(': ')) > 1: dataToFile.append(line.split(': ')[1].strip('\n'))
                    elif line.startswith('Linked Media File:'): 
                        lineSplit = line.split(':')[1].strip('\n').strip(' ')
                        if ',' in lineSplit:
                            for attachment in lineSplit.split(','): dataToFile.append(f'''=HYPERLINK("{attachment}")''')
                        else: dataToFile.append(f'''=HYPERLINK("{lineSplit}")''')
            print(f'---All data added to thread_{threadID}.csv. All Files Created.')
            
def main():
    # Check if an HTML file path was provided (via drag-and-drop or command line)
    if len(sys.argv) < 2:
        # Get the directory where the script is located
        scriptDir = os.getcwd()
        
        # Set the path for 'records.html' in the same directory as the script
        defaultHtmlFile = os.path.join(scriptDir, 'records.html')
        
        # Check if 'records.html' exists in the same directory
        if os.path.exists(defaultHtmlFile):
            htmlFilePath = defaultHtmlFile
            print(f"No file provided. Using 'records.html' found in script directory: {htmlFilePath}")
        else:
            print("Error: No HTML file provided and 'records.html' not found in the script's directory.")
            return
    else:
        # Get the HTML file path from command-line arguments
        htmlFilePath = os.path.normpath(sys.argv[1])

    # Ensure the file has an .html extension
    if not htmlFilePath.endswith('.html'):
        print("Error: Provided file is not an HTML document.")
        return

    # Set the output text file path in the same directory as the input HTML file
    outputTextFilePath = os.path.join(os.path.dirname(htmlFilePath), 'stripped_data.txt')

    # Identify keywords for future cleanup
    keywords = ['Current Participants', 'Author', 'Sent', 'Body', 'Text', 'Url', 'URL', 'Type', 'Size', 'Attachments', 'Users']

    # Extract the section to a text file
    extractSectionToText(htmlFilePath, outputTextFilePath, keywords)

    # Clean up the mess in the text file from the bad div elements
    strippedDataCleanup(outputTextFilePath)

    # Make CSVs
    dataToThreadList(outputTextFilePath)

    done = input('Complete. Press ENTER to exit.')

if __name__ == "__main__":
    main()
