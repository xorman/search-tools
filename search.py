#!/usr/bin/env python3
""" A tool that generates and invokes find and grep commands. """
########################################################################
# Prerequisites: find, grep, and python3 must be installed on
# the system. This script was tested on a vanilla Linux and macOS.
# On Windows it was tested with GitBash and Python3 installed.
# [This contains GitBash](https://git-for-windows.github.io/)
# To run this script in GitBash, please create or extend
# ~/.bash_profile with:
# PATH="$PATH:/c/Users/$(whoami)/AppData/Local/Programs/Python/Python39/"
# # or this if 32 bit Python interpreter is installed
# PATH="$PATH:/c/Users/$(whoami)/AppData/Local/Programs/Python/Python39-32/"
# export PATH
# Furthermore, it might be necessary to change python3 to python in
# the shebang line.
########################################################################
# Copyright 2020 Norman MEINZER
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
########################################################################
import sys
import os
import platform
import subprocess
import shlex
from textwrap import dedent
from argparse import ArgumentParser, RawDescriptionHelpFormatter, RawTextHelpFormatter
__author__  = 'Norman MEINZER'
__email__   = 'real.norman.meinzer@gmail.com'
__twitter__ = 'https://twitter.com/xor_man'
__license__ = 'GPLv3'


if sys.version_info.major == 2:
    # Python2's input() is vulnerable to code injection by design.
    # It accepts Python commands and executes them. Python2's raw_input()
    # is not vulnerable. Therefore, always use raw_input() in Python2.
    # Python2's raw_input() does what input() does in Python3.
    input = raw_input


def main():
    search = Search()
    search.parse_arguments()
    search.prepare_arguments_for_find()
    search.prepare_arguments_for_grep()
    search.prepare_list_of_paths_to_search_in()
    search.invoke_command()


class Search(object):
    """ Core class of this search script. Implements methods that parse user input
    and methods that create comprehensive command line arguments which are
    finally processed by the applications find and grep.
    """
    def __init__(self):
        self.name = os.path.basename(sys.argv[0])
        self.grep_file_size_threshold = '-size -2000k '
        if platform.system() == 'Windows':
            self.grep_terminator = ';'
            tmp = '~/' + os.path.splitext(self.name)[0]
            paths_config_root_path = os.path.expanduser(tmp)
            if not os.path.exists(paths_config_root_path):
                # Create the hidden config folder in ~
                os.makedirs(paths_config_root_path)
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(paths_config_root_path, 0x2)
            self.paths_config_path = paths_config_root_path + '/default-paths/'
        else:
            self.grep_terminator = '\;'
            self.paths_config_path = '~/.' + os.path.splitext(self.name)[0] + '/default-paths/'
    def parse_arguments(self):
        parse_arguments(self)
    def prepare_arguments_for_find(self):
        prepare_arguments_for_find(self)
    def prepare_arguments_for_grep(self):
        prepare_arguments_for_grep(self)
    def prepare_list_of_paths_to_search_in(self):
        prepare_list_of_paths_to_search_in(self)
    def create_file_type_categories(self):
        create_file_type_categories(self)
    def find_file_type_cat_or_exit(self):
        return find_file_type_cat_or_exit(self)
    def invoke_command(self):
        invoke_command(self)
    def parse_default_paths_from_file(self, id):
        parse_default_paths_from_file(self, id)
    def add_file_ext_filter(self, file_type_category, file_pattern):
        add_file_ext_filter(self, file_type_category, file_pattern)
    def add_time_filter(self):
        add_time_filter(self)


def parse_arguments(self):
    """ Parse user input from the command line, define default settings for
    some arguments, specify choices for arguments that have predictable
    input.
    """
    parser = ArgumentParser(
        # formatter_class=RawDescriptionHelpFormatter,
        formatter_class=RawTextHelpFormatter,
        description=dedent("""
            Offline search tool for files and file content of files that are not indexed.
            The goal of this tool is to keep the search command as short as possible. The
            script generates (arg -s) and invokes a tailored find and grep command
            with a selection of switches enabled by default. Some switches should
            increase the search speed but might also exclude relevant search results. For
            instance, argument -g only searches patterns in files with {}.""".format(
            self.grep_file_size_threshold)),
        epilog=dedent("""
            Examples:
                {0} . '*.txt' --grep pattern
                {0} . -s > s.sh; chmod +x s.sh; ./s.sh
                {0} . -f text,sc""".format(self.name)))
    parser.add_argument(
        'search_path', nargs='?', default='.',
        help='Search path that is passed to the find application')
    # This was necessary for a GitBash-constellation that I don't recall.
    # if platform.system() == 'Windows':
    #     file_pattern_default = '\*'
    # else:
    #     file_pattern_default = '*'
    file_pattern_default = '*'
    parser.add_argument(
        'file_pattern', nargs='?', default=file_pattern_default,
        help='File pattern that is passed to `find`')
    parser.add_argument(
        '-g', '--grep', action='store',
        help='File content search of pattern (passed to `grep`)')
    parser.add_argument(
        '-d', '--default-path-file', action='store', nargs='?',
        const='default-list',
        help=dedent("""
            Reads a list of search paths from a config file
            named DEFAULT_PATH_FILE and stored in
            {0}.
            Then, runs the generated command for each path.
            Asks for interactive creation of the config file if
            it doesn't exist. If the positional arg file_pattern
            is used, the arg search_path remains mandatory but
            will be overwritten by the list created through -d
            arg. E.g. {1} . '*.xyz' -s -d""".format(
            self.paths_config_path, self.name)[1:]))
    parser.add_argument(
        '-f', '--file-type',
        # action='store', choices=self.file_type_choices,
        help=dedent('''
            Search for a category of file types. A category is a
            collection of file extensions plus an optional file size.
            Supports comma separated list like 'text,audio'. Prints
            a list of available type categories if FILE_TYPE is
            unknown.'''[1:]))
    parser.add_argument(
        '-s', '--show-command', action='store_true',
        help="Show generated command. Don't invoke it.")
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='Print separator and generated command, then invoke it')
    parser.add_argument(
        '-m', '--more-context', action='store', nargs='?', const='4',
        help='Print context lines before and after `grep` match')
    parser.add_argument(
        '-l', '--last-modified',
        action='store', choices=['y', 'q', 'm', 'w', 'd', 't'],
        help=dedent('''
            Last modified within the past [ Year, Quarter,
            Month, Week, Day(24h), Today(12h) ]''')[1:])
    parser.add_argument(
        '-c', '--case-sensitive',
        action='store_true',
        help='Case sensitive search for `find` (and `grep`)')
    self.args = parser.parse_args()

    self.args.search_path = self.args.search_path.replace('"', '\\"')
    self.args.file_pattern = self.args.file_pattern.replace('"', '\\"')
    if self.args.grep:
        self.args.grep = self.args.grep.replace('"', '\\"')

    if not self.args.case_sensitive:
        self.case_insensitive = 'i'
    else:
        self.case_insensitive = ''


def prepare_arguments_for_find(self):
    """ Prepare the options that are passed to the find executable. """
    self.find_arg = '-not -path \'*/.git/*\' '
    # File types / names ------------------
    if self.args.file_type:
        # Search for one or more categories of file types.
        # Categories can be text, image, audio OR not-text.
        self.create_file_type_categories()

        file_type_cats = self.find_file_type_cat_or_exit()
        if len(file_type_cats) == 1 and file_type_cats[0]['size'] != '':
            # `find` only takes one -size argument. Therefore,
            # it is only passed if the user searches one of our
            # file type categories.
            self.find_arg += '-size ' + file_type_cats[0]['size'] + ' '
        self.add_file_ext_filter(file_type_cats, self.args.file_pattern)
    else:
        # Search for one file pattern (e.g. *.py)
        self.find_arg+='-' + self.case_insensitive + 'name \'' + self.args.file_pattern + '\' '
        #if self.args.regex:
        #    self.find_arg+='-regextype "posix-extended" -' + self.case_insensitive \
        #                + 'regex \'' + self.args.file_pattern + '\' '
        #else:
        #    self.find_arg+='-' + self.case_insensitive + 'name \'' + self.args.file_pattern + '\' '

    # Time --------------------------------
    if self.args.last_modified:
       self.add_time_filter()


def prepare_arguments_for_grep(self):
    """ Prepare the options that are passed to the grep executable. """
    self.grep_arg = '-exec grep --color=always '
    self.grep_arg += '--with-filename --line-number '
    if self.args.more_context is not None:
        self.grep_arg += '--before-context=' + self.args.more_context + ' '
        self.grep_arg += '--after-context=' + self.args.more_context + ' '


def prepare_list_of_paths_to_search_in(self):
    """ Prepares the paths in which `find` will search. """
    if self.args.default_path_file is not None:
        # `find` will be invoked for each path
        self.parse_default_paths_from_file( self.args.default_path_file )
    else:
        # `find` will be invoked once
        self.paths = [ self.args.search_path ]


def create_file_type_categories(self):
    """ This is an embedded configuration of file_type categories.

    A file_type category consists of size, the match-flag, and extensions.
    - size : Optional criteria to reduce the number of file findings
             through the file size.
    - match: True  --> Find files that match the extensions
             False --> Find files that don't match the extensions.
                       These entries are automatically generated.
    - extensions: Mandatory list of file extensions to search for.
    """
    # TODO too many matches with 'import mimetypes'?
    self.file_type_categories = {
        'text' :
            { 'size' : '', 'match' : True, 'extensions' :
                ('txt', 'md', 'markdown', 'csv', 'url') },
        'markup-text' :
            { 'size' : '', 'match' : True, 'extensions' :
                ('tex', 'htm', 'html', 'rtf') },
        'code' :
            { 'size' : '', 'match' : True, 'extensions' :
                ('c', 'cpp', 'cc', 'h', 'hpp', 'java', 'swift', 'php', 'rb', 'el', 'lsp', 'm', 'cp') },
        'configuration' :
            { 'size' : '', 'match' : True, 'extensions' :
                ('cfg', 'reg', 'yaml', 'ini', 'xml', 'json') },
        'script' :
            { 'size' : '', 'match' : True, 'extensions' :
                ('sh', 'py', 'pl', 'mk', 'mak', 'cmake', 'bat', 'ps1', 'vb', 'vbs', 'ws', 'scpt', 'command', 'tcl', 'vim', 'r', 'lua') },
        #'' :
            #{ 'size' : '', 'match' : True, 'extensions' : ( '', '' ) },
        'image' :
            { 'size' : '+4k',  'match' : True, 'extensions' :
                ('png', 'jpg', 'bmp', 'gif', 'jpeg', 'svg', 'tif', 'tiff') },
        'audio' :
            { 'size' : '+10k', 'match' : True, 'extensions' :
                ('mp3', 'wma', 'ogg', 'wav', 'midi', 'aif') },
        'video' :
            { 'size' : '+500k','match' : True, 'extensions' :
                ('avi', 'mkv', 'mpg', 'mpeg', 'h264', 'mov', 'mp4', 'vob', 'flv', '3gp', 'wmv') },
        'certificate' :
            { 'size' : '',   'match' : True, 'extensions' :
                ('cer', 'crt', 'der', 'pem', 'crl') },
        # TODO use zipfile.is_zipfile() and tarfile.is_tarfile() instead?
        'archive' :
            { 'size' : '',   'match' : True, 'extensions' :
                ('7z', 'zip', 'gz', 'tgz', 'z', 'rar', 'rpm', 'pkg', 'deb') }
    }

    # Auto generate 'not-' / match=False entries
    not_file_type_categories = dict()
    self.file_type_choices = list()
    for file_type_key, file_type_cat in self.file_type_categories.items():
        self.file_type_choices += [ file_type_key ]
        if not file_type_key.startswith('not-'):
            file_type_not_key = str('not-') + file_type_key
            self.file_type_choices += [ file_type_not_key ]
            not_file_type_categories[ file_type_not_key ] = dict(file_type_cat)
            not_file_type_categories[ file_type_not_key ]['match'] = False
    self.file_type_categories.update(not_file_type_categories)


def find_file_type_cat_or_exit(self):
    """ Parses the -f command line argument operand and tries to
    find the internal definition of the requested type. Prints a
    list of available types if the requested type was not found
    and exits.
    """
    file_type_cats = []
    for file_type in self.args.file_type.split(','):
        file_type_cat = False
        for file_type_key in self.file_type_categories:
            if file_type_key.startswith(file_type):
                file_type_cat = self.file_type_categories[ file_type_key ]
                break

        if file_type_cat:
            file_type_cats.append(file_type_cat)
        else:
            sys.stdout.write("Error: Unknown file-type '" + self.args.file_type + "'; choices: ")
            print(self.file_type_choices)
            exit(1)
    return file_type_cats


def add_file_ext_filter(self, file_type_categories, file_pattern):
    """ Reduce the number of file findings by searching for a specific
    'file_pattern' (wildcards supported) and 'file_type_categories'.
    """
    self.find_arg += '\( '
    first_type = True
    for file_type_category in file_type_categories:
        extensions = file_type_category['extensions']
        if file_type_category['match'] == False:
            if not first_type:
                self.find_arg += '-o '
            self.find_arg += '-not -' + self.case_insensitive + 'name \'' + \
                             file_pattern + '.' + extensions[0] + '\' '
            for ext in extensions[1:]:
                self.find_arg += '-a -not -' + self.case_insensitive + 'name \'' + \
                                 file_pattern + '.' + ext + '\' '
        else:
            if not first_type:
                self.find_arg += '-o '
            self.find_arg += '-' + self.case_insensitive + 'name \'' + \
                             file_pattern + '.' + extensions[0] + '\' '
            for ext in extensions[1:]:
                self.find_arg += '-o -' + self.case_insensitive + 'name \'' + \
                              file_pattern + '.' + ext + '\' '
        first_type = False
    self.find_arg += ' \) '


def add_time_filter(self):
    """ Reduce the number of file findings by searching for files that
    were last modified N hours ago or afterwards. N is derived from an
    argument that is stored in a member of the class.
    """
    lm_dict = {
        'y': '-mtime -365 ',
        'q': '-mtime -90 ',
        'm': '-mtime -30 ',
        'w': '-mtime -7 ',
        'd': '-mtime -1 ',
        't': '-mmin -720 ' # 720 minutes ago = 12 hours
    }
    # Input is already validated by argparser choices
    self.find_arg += lm_dict[ self.args.last_modified ]

    # File modification within a time frame
    #min_date='2010-12-31'
    #max_date='2011-12-31'
    #self.find_arg += '-newermt $min_date ! -newermt $max_date ' # Modifies between


def parse_default_paths_from_file(self, id):
    """ Read a list of paths from a configuration file. One path per
    line. No new line after last path. Multiple files are supported.
    File is selected by an 'id'. If the file does not exist, the
    user is asked to create it interactively.
    """
    self.paths = list()
    file_name = os.path.expanduser(self.paths_config_path) + id + '.txt'
    try:
        tmp_file = open(file_name)
        for path in tmp_file:
            path_to_add = path.rstrip().replace('"', '\\"')
            path_to_add = os.path.expanduser( path_to_add )
            self.paths += [ path_to_add ]
    except:
        print('Configuration file ' + file_name + ' does not exist.')
        if dialog_yes_no('Do you want to create it?', 'no'):
            try:
                if not os.path.exists( os.path.dirname(file_name) ):
                    os.makedirs( os.path.dirname(file_name) )
                tmp_file = open(file_name, 'w')
                print('Please enter one path, then press enter. Enter empty line to exit.')
                new_path = input()
                while new_path != '':
                    tmp_file.write(new_path)
                    new_path = input()
                    if new_path != '':
                        tmp_file.write('\n')
            except:
                print('Cannot open file for writing')


def invoke_command(self):
    """
    The final assembly and invokation of the command happens here
    """
    for path in self.paths:
        command='find \'' + path + '\' ' + self.find_arg

        if self.args.grep:
            command += ' -type f '
            if not '-size' in command:
                # If grep is used, ensure that a file '-size' limit is set. This
                # prevents that time is wasted for a pattern search in big files
                # that are often compressed or encrypted archives.
                command += self.grep_file_size_threshold

            command += self.grep_arg
            if not self.args.case_sensitive:
                command += '--ignore-case '
            command += '\'' + self.args.grep + '\'' + ' {} ' + self.grep_terminator
        else:
            if self.args.more_context is not None:
                print('Warning: Option -m,--more-context is only effective in '
                      'combination with -g')
        if self.args.verbose:
            terminal_rows, terminal_columns = os.popen('stty size', 'r').read().split()
            print( '#' * int(terminal_columns) )
        if self.args.verbose or self.args.show_command:
            print(command)
        if not self.args.show_command:
            #print( os.popen(command).read() )
            execute_and_print_stdout_while_running(command)


def execute_and_print_stdout_while_running(command):
    """ Executes a shell 'command' and prints the standard
    output of the subprocess while it is running. Returns
    after the subprocess exited.
    """
    # Popen() observations
    # ====================
    # subprocess.Popen(command=, shell=, ...)
    # Try not to use shell=True! Please refer to security warning at
    # <https://docs.python.org/2/library/subprocess.html#popen-constructor>
    #
    # Popen() in GitBash on Windows 10
    # --------------------------------
    # - shell=False
    #     - Parameter command is passed to cmd.exe
    # - shell=True
    #     - Parameter command is passed to bash
    #     - command is of type string
    # - Example: find "." \( -iname "*.sh" -o -iname "*.py" \)
    #     - Here, Popen() doesn't accept double quotes with parameter shell=True.
    #       Therefore, 'Quote\'' is used instead of "Quote'" in this script.
    # Popen() on Linux
    # ----------------
    # command is of type list. TODO: I think these worked:
    # cmd = [ 'find', '.', '\\(',  '-iname', '\\*.sh', '-o', '-iname', '\\*.py', '\\)' ]
    # or ...
    # cmd = [ 'find', '.', '\\(',  '-iname', '\'*.sh\'', '-o', '-iname', '\'*.py\'', '\\)' ]
    if platform.system() == 'Windows':
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    else:
        process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    while True:
        try:
            line = process.stdout.readline().decode('utf-8')
            if process.poll() is not None and '' == line:
                break
            sys.stdout.write(line)
            sys.stdout.flush()
        except:
            sys.stderr.write('Cannot process line properly\n')


def dialog_yes_no(question, default_answer=None):
    """ Yes/No user dialog that asks the 'question' and returns
    True for yes and False for no. If a 'default_answer' is
    passed to this function, the user can just hit enter to
    continue with this answer. The default answer is indicated
    through capitalization in the prompt.
    Inspired by: <http://code.activestate.com/recipes/577058/>
    """
    valid_answers = { "yes": True, "ye": True, "y": True,
                      "no": False, "n": False }
    if default_answer is None:
        prompt = '[y/n]'
    elif 'yes' == default_answer:
        prompt = '[Y/n]'
    elif 'no' == default_answer:
        prompt = '[y/N]'
    else:
        raise ValueError("Invalid default answer '%s'" % default_answer)

    while True:
        sys.stdout.write(question + ' ' + prompt + ' ')
        answer = input().lower()
        if answer == '' and default_answer is not None:
            return valid_answers[default_answer]
        elif answer in valid_answers:
            return valid_answers[answer]
        else:
            print("Please respond with 'yes' or 'no'")


if __name__ == '__main__':
    main()

