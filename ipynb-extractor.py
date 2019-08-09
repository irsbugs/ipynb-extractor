#!/usr/bin/env python3
#
# ipynb-extractor.py
#
# Objectives:
# o Read a Jupyter notebook ipynb file using simplejson module.
# o Create a folder based on the filename of the ipynb file.
# o Extract the data from the markdown and code cells in the ipynb file.
# o Write into the folder the data as markdown or python files.
#
# Ian Stewart
# 2019-08-09
#
import sys
import os
import shutil
try:
    import simplejson as json
except ImportError:
    import json

VERSION = "0.1"

HEADING = ("\nRead a Jupyter notebook (.ipynb) file and extract to a folder \n"
            "the markdown and code cells as markdown.md and python.py files.")


def query_user_bool(prompt="Proceed?", default=True,):
    # Submit a boolean query to the User. Return True or False
    # No need for a while loop
    yes_tuple = ("y", "t", "1")
    no_tuple = ("n", "f", "0")
    # Build the prompt as [Y/n] or [N/y]
    if default:
        prompt = prompt + " [Y/n]: " 
        response = input(prompt)
        if response == "": response = "y"
        if response.lower()[0] in yes_tuple:
            return True
        else:
            return False
    else:
        prompt = prompt + " [N/y]: "
        response = input(prompt)
        if response == "": response = "n"
        if response.lower()[0] in no_tuple:
            return False
        else:
            return True


def get_file_list(extension):
    # In the current working directory get a list of all files and from it
    # create a file_list with only the desired extension. 
    cwd = os.getcwd()
    file_list_all = sorted(os.listdir(cwd))
    # print(len(file_list))
    file_list = []
    for index, file_name in enumerate(file_list_all):
        if file_name.split(".")[-1] == extension:  # ipynb
            # print(file_name)
            file_list.append(file_name)
    return file_list


def query_user_menu(menu_list, prompt=None, default=1):
    # User selects from a list. Return an index into the list
    if len(menu_list) == 0:
        return -1
    print()
    for index, item in enumerate(menu_list):
        print("{:>3}. {}".format(index + 1, item))
    if prompt == None:
        prompt = ("\nEnter the number of the item [{}]: "
                .format(default))
    else:
        prompt = ("\n{} [{}]: ".format(prompt, default))

    while True:     
        response = input(prompt)
        if response == "": response = default
        try:
            response = int(response)
            if response < 1 or response > len(menu_list):
                print("Invalid.  Requires a value between {} and {}"
                    .format(1, len(menu_list)))
                continue
            else:
                return response - 1
        except ValueError as e:
            print("Value Error. Requires a value between {} and {}"
                    .format(1, len(menu_list)))
            continue


def select_files(extension):
    # Select which ipynb files to modify
    file_list = get_file_list(extension)

    prompt = "Select the ipynb file for extraction of cells"
    index = query_user_menu(file_list, prompt)
    # If no files with extension type were found then -1 is returned
    if index == -1:
        sys.exit("No files with extension of .{} were found. Exiting"
                .format(extension))
    return file_list[index]


def display_help():
    # Print either the brief or the full help and exit
    if sys.argv[1] == "-h":
        print(HELP_BRIEF)
    else:
        print(HELP_FULL)
    sys.exit()


def start_interactive():
    # No arguments were passed with the commmand line so use menu driven.
    # Call functions to produce a menu of ipynb files.
    extension = "ipynb"
    file_selected = select_files(extension)
    print("File selected for extraction of cells: {}".format(file_selected))
    file_list = []
    file_list.append(file_selected)
    extract(file_list)


def extract(file_list):
    # From a list of files, create folders and extract cells as markdown .md or
    # python .py files.
    for file_name in file_list:
        with open(file_name, "r") as fin:
            # Using the ipynb files name, use name to create a folder.
            folder_name = os.path.splitext(file_name)[0]
            #print(folder_name)
            # Make a folder off the cwd
            cwd = os.getcwd()
            #print(cwd)
            folder_path = cwd + os.sep + folder_name
            # If the folder exists remove it and any files in it.
            if os.path.isdir(folder_path):
                print("Folder `{}` already exists".format(folder_name))
                prompt = "Delete contents of folder?"
                response = query_user_bool(prompt, False,)
                if response:
                    shutil.rmtree(folder_path)
                else:
                    sys.exit("Opted not to delete folder. Unable to continue.")
            # Create the folder
            os.mkdir(folder_path)
            print("Created folder `{}`.".format(folder_name))  

            # Use json to load the ipynb file as "data"
            data = json.load(fin)    
            cell_total = len(data["cells"]) 
            print("ipynb file: {}, total cells: {}".format(file_name, cell_total))

            markdown_count = 0
            code_count = 0
            for i in range(cell_total):
                #print(data["cells"][i]["cell_type"])  # code or markdown
                cell_type = data["cells"][i]["cell_type"]

                if cell_type == "markdown": markdown_count += 1
                if cell_type == "code": code_count += 1

                #print(data["cells"][i]["source"])
                for item in data["cells"][i]["source"]:
                    #print(item[:-1])  # remove the additional newlines
                    # Build the path and filename for file to extract to
                    extracted_file = ("{}{}{}_{:02d}"
                            .format(folder_path, os.sep, folder_name, i + 1))
                    if cell_type == "markdown":
                        extracted_file = extracted_file + ".md" 
                    elif cell_type == "code":
                        extracted_file = extracted_file + ".py"
                    else:
                        # Don't support "raw" or other cell types.
                        # Skip cell and continue. Miss out one filename number
                        print("Cell Type: {} is invalid. Skipping this cell."
                                .format(cell_type)) 
                        continue
                    # Write the cells "source" to the file.
                    with open(extracted_file, "w") as fout:
                        for item in data["cells"][i]["source"]:
                            fout.write(item) 
            print("ipynb file: `{}` cells extracted to folder `{}`\n"
                    "Markdown files: {}, Python files: {}"
                    .format(file_name, folder_name, markdown_count, code_count))
      

def main():
    print(HEADING)
    # Check for args
    if len(sys.argv) == 1:
        # go to start interactive
        start_interactive()

    if len(sys.argv) > 1:
        # Second argument may be help option
        if sys.argv[1].startswith("-h") or sys.argv[1].startswith("--h"):
            display_help()
            sys.exit()

        # Second+ argument(s) should be an ipynb file or list of ipynb files
        #file_list = []
        #for i in range(1, len(sys.argv)):
        #    #print(sys.argv[i])
        #    file_list.append(sys.argv[i])

        # The above loop can be done as follows:
        # pop(0) the sys.argv list, then its only a list of file names or -h
        sys.argv.pop(0) # Get rid of python program file name from list
        #print(sys.argv)    
        file_list = sys.argv
        #print(file_list)    

        # Files must have .ipynb extension.
        for file_name in file_list:
            if not file_name.split(".")[-1] == "ipynb":
                sys.exit("ERROR: Must be a .ipynb file. File {} is not valid."
                        .format(file_name))

        # Check files exist in cwd / exit if the don't exist.
        #print(file_list)
        cur_dir = os.getcwd()
        folder_list = os.listdir(cur_dir)
        for file_name in file_list:
            if file_name in folder_list:
                print("{} exists in: {} ".format(file_name, cur_dir))
                continue
            else:          
                sys.exit("{} not in directory {}.".format(file_name, cur_dir))        

        extract(file_list)


if __name__ == "__main__":

    if sys.version_info[0] != 3:
        sys.exit("Please use python version 3. Exiting...")

    print("\nipynb-extractor version: {}".format(VERSION))


# Put the Constants with lots of text at the end. Makes the code easier to read.

HELP_FULL = """Usage: ipynb-extractor [OPTION]... [FILE]...

From Jupyter notebook ipynb file(s) extract the markdown and code cells.
Create a folder based on the ipynb filename. Extract to the folder the
code cells as python (.py) files or as markdown (.md) files.

[OPTION]...
Options and arguments:
   -h       print a brief help message and exits. 
   --help   print this full help message and exits.

[FILE]...
If no files are provided as arguments then the program will run in a menu 
driven mode and prompt you to select a Jupyter notebook (.ipynb) file.

Any file with a .ipynb extension in the current working directory may be 
provided as an argument. A folder is created based on the ipynb file name.

A list of space separated files may be provided. One folder will be created 
for each ipynb file.

The files may be selected by wild-carding with *, or *.ipynb. E.g.
$ ipynb_creator *.ipynb


Notes / Example:

If the current working directory already has a folder with the ipynb file, 
prompting is performed to determine if you wish to over-write the folder.

The ipynb_creator utility provides an example of reading a text file and
creating an ipynb file. As an example the ipynb-extractor utility may be 
used on this ipynb file:

$ python3 ipynb-extractor.py help_text_example.ipynb

ipynb-extractor version: 0.1

Read a Jupyter notebook (.ipynb) file and extract to a folder 
the markdown and code cells as markdown.md and python.py files.

Created folder `help_text_example`.
ipynb file: help_text_example.ipynb, total cells: 5
ipynb file: `help_text_example.ipynb` cells extracted to folder `help_text_example`
Markdown files: 3, Python files: 2

$ ls -1 help_text_example/
help_text_example_01.md
help_text_example_02.py
help_text_example_03.md
help_text_example_04.py
help_text_example_05.md

$ cat help_text_example/help_text_example_04.py
import math
a = 2
print(math.sqrt(a))


Author: Ian Stewart - 9 August 2019.
"""

HELP_BRIEF = """Usage: ipynb-extractor [OPTION]... [FILE]...

From Jupyter notebook ipynb file(s) extract the markdown and code cells.
Create a folder based on the ipynb filename. Extract to the folder the
code cells as python (.py) files or as markdown (.md) files.

[OPTION]...
Options and arguments:
   -h       print this brief help message and exit. 
   --help   print a full help message and exit.

[FILE]...
If no files are provided as arguments then the program will run in a menu 
driven mode and prompt you to select a Jupyter notebook (.ipynb) file.

Any file with a .ipynb extension in the current working directory may be 
provided as an argument. A folder is created based on the ipynb file name.

A list of space separated files may be provided. One folder will be created 
for each ipynb file.

The files may be selected by wild-carding with *, or *.ipynb. E.g.
$ ipynb_creator *.ipynb
"""

# Continue by calling the main() function routine
main()

