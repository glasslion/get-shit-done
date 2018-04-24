# -*- coding: utf-8 -*-
import glob
import os
import urllib


def confirm(text):
    answer = raw_input(text)
    answer = answer.lower()
    return answer == 'y' or answer == 'yes'


def main():
    dir_path = raw_input(
        "Please enter the directory path [~/Downloads ]:")
    dir_path =  dir_path or '~/Downloads/'
    dir_path = os.path.expanduser(dir_path)
    os.chdir(dir_path)
    files = glob.glob('%E*')
    for file in files:
        decoded = urllib.unquote_plus(file)
        if confirm("Do you want to rename {} to {}? [yes|no]".format(file, decoded)):
            os.rename(file, decoded)


if __name__ == '__main__':
    main()