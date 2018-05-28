#!/usr/bin/env python
""" A tool that generates and invokes `find` and `grep` commands. """
########################################################################
# Description  : Please refer to the command line help (-h)
# Prerequisites: `find`, `grep`, and `python2 or 3` must be installed on
# the system. This script was tested on a vanilla Linux and macOS.
# On Windows it was tested with GitBash and Python installed.
# <https://git-for-windows.github.io/> contains GitBash
# <https://www.python.org/downloads/>
# To run this script in the GitBash with ./, please create the following
# file in %HOMEPATH%.       File_name: .bash_profile            Content:
# PATH=$PATH:/c/Users/$(whoami)/AppData/Local/Programs/Python/Python36/
# PATH=$PATH:/c/Users/$(whoami)/AppData/Local/Programs/Python/Python36-32/
# export PATH
########################################################################
# Copyright 2017 Norman MEINZER
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
import argparse
import os
import platform
import subprocess
import shlex 
__author__  = 'Norman MEINZER'
__email__   = 'meinzer.norman@gmail.com'
__twitter__ = 'https://twitter.com/xor_man'
__license__ = 'GPLv3'


class Search(object):
    """ Core class of this search script. Implements methods that parse user input 
    and methods that create comprehensive command line arguments which are 
    finally processed by the applications `find` and `grep`.
    """
    def __init__(self):
        self.find_arg = ''
        self.grep_arg = '-exec grep --color=always '
        self.grep_arg += '-H -n '   # Show file name (-H) and line number (-n)
        self.grep_file_size_threshold = '-size -2000k '
        self.name = os.path.basename(sys.argv[0])  
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
        #self.create_file_types()
    def parse_arguments(self):
        parse_arguments(self)
    def create_file_types(self):    
        create_file_types(self)
    def find_file_type_def_or_exit(self):
        return find_file_type_def_or_exit(self)
    def invoke_command(self):    
        invoke_command(self)
    def parse_default_paths_from_file(self, id):
        parse_default_paths_from_file(self, id)
    def add_file_ext_filter(self, file_type_definition, file_pattern):
        add_file_ext_filter(self, file_type_definition, file_pattern)
    def add_time_filter(self):
        add_time_filter(self)


def parse_arguments(self):
    """ Parse user input from the command line, define default settings for
    some arguments, specify choices for arguments that have predictable
    input.
    """
    parser = argparse.ArgumentParser(
        description = 'Offline search tool for files and file content of files that are not indexed. '
                      'The goal of this tool is to keep the search command as short as possible. The '
                      'script generates (arg -s) and invokes a tailored `find` and `grep` command '
                      'with a selection of switches enabled by default. Some switches should '
                      'increase the search speed but might also exclude relevant search results. For '
                      'instance, argument -g only searches patterns in files with ' + 
                      self.grep_file_size_threshold,
        epilog = 'Examples: ' + self.name + " . '*.txt' --grep pattern "
                + '________________________________ '
                + self.name + " -s > s.sh; chmod +x s.sh; ./s.sh"
                + ' __________________________________ '
                + self.name + " -f text,sc"
                #+ ' ___________________________________________________________ '
                #+ self.name + " -r '.*a.*l\.(png|jpg|bmp|ico)'"
    )
    parser.add_argument('search_path', nargs='?', default='.',
                        help='Search path that is passed to the `find` application')
    parser.add_argument('file_pattern', nargs='?', default='*', 
                        help='File pattern that is passed to `find`')
    parser.add_argument('-g', '--grep', help='File content search of pattern (passed to `grep`)', 
                        action='store')
    parser.add_argument('-d', '--default-path-file', help='Reads a list of search paths from a config '
                        'file named DEFAULT_PATH_FILE and stored in ' + self.paths_config_path + 
                        '. Then, runs the generated command for each path. '
                        'Asks for interactive creation of the config file if it doesn\'t exist. '
                        'If the positional arg file_pattern is used, the arg search_path remains '
                        'mandatory but will be overwritten by the list created through -d arg. '
                        'E.g. ' + self.name + ' . \'*.xyz\' -s -d'
                        , action='store', nargs='?', const='default-list')
    parser.add_argument('-f', '--file-type', help='Select a search file type (= file extensions + size). ' +
                        'Supports comma separated list. Prints list of available types if FILE_TYPE is unknown.') #,
                        #action='store', choices=self.file_type_choices)
    parser.add_argument('-s', '--show-command', help="Show generated command. Don't invoke it.",
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Print separator and generated command, then invoke it',
                        action='store_true')
    parser.add_argument('-m', '--more-context', help='Print context lines before and after `grep` match',
                        action='store', nargs='?', const='4')
    parser.add_argument('-l', '--last-modified', help= 'Last modified within the past [ Year, Quarter, ' +
                        'Month, Week, Day(24h), Today(12h) ]',
                        action='store', choices=['y', 'q', 'm', 'w', 'd', 't'])
    parser.add_argument('-c', '--case-sensitive', help='Case sensitive search for `find` (and `grep`)',
                        action='store_true')
    self.args = parser.parse_args()
    
    self.args.search_path = self.args.search_path.replace('"', '\\"')
    self.args.file_pattern = self.args.file_pattern.replace('"', '\\"')
    if self.args.grep:
        self.args.grep = self.args.grep.replace('"', '\\"')


def create_file_types(self):    
    """ This is an embedded configuration of file_types. 
    A file_type consists of 'size', the 'match'-flag, and 'extensions'.
    - size : Optional criteria to reduce the number of file findings
             through the file size.
    - match: 'True'  --> Find files that match the 'extensions'
             'False' --> Find files that don't match the 'extensions'.
                         These entries are automatically generated.
    - extensions: Mandatory list of file extensions to search for.
    """
    # TODO too many matches with 'import mimetypes'?
    self.file_types = { 
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
    not_file_types = dict()
    self.file_type_choices = list()
    for file_type_key, file_type_def in self.file_types.items():
        self.file_type_choices += [ file_type_key ]
        if not file_type_key.startswith('not-'):
            file_type_not_key = str('not-') + file_type_key
            self.file_type_choices += [ file_type_not_key ]
            not_file_types[ file_type_not_key ] = dict(file_type_def)
            not_file_types[ file_type_not_key ]['match'] = False
    self.file_types.update(not_file_types)


def find_file_type_def_or_exit(self):
    """ Parses the -f command line argument operand and tries to
    find the internal definition of the requested type. Prints a 
    list of available types if the requested type was not found
    and exits.
    """
    file_type_defs = []
    for file_type in self.args.file_type.split(','):
        file_type_def = False
        for file_type_key in self.file_types:
            if file_type_key.startswith(file_type):
                file_type_def = self.file_types[ file_type_key ]
                break

        if file_type_def:
            file_type_defs.append(file_type_def)
        else:
            sys.stdout.write("Error: Unknown file-type '" + self.args.file_type + "'; choices: ")
            print(self.file_type_choices)
            exit(1)
    return file_type_defs


def add_file_ext_filter(self, file_type_definitions, file_pattern):
    """ Reduce the number of file findings by searching for a specific 
    'file_pattern' (wildcards supported) and 'file_type_definitions'.
    """
    self.find_arg += '\( '
    first_type = True
    for file_type_definition in file_type_definitions:
        extensions = file_type_definition['extensions']
        if file_type_definition['match'] == False:
            if not first_type:
                self.find_arg += '-o '
            self.find_arg += '-not -' + self.case_insensitive + 'name "' + \
                             file_pattern + '.' + extensions[0] + '" '
            for ext in extensions[1:]:
                self.find_arg += '-a -not -' + self.case_insensitive + 'name "' + \
                                 file_pattern + '.' + ext + '" '
        else:
            if not first_type:
                self.find_arg += '-o '
            self.find_arg += '-' + self.case_insensitive + 'name "' + \
                             file_pattern + '.' + extensions[0] + '" '
            for ext in extensions[1:]:
                self.find_arg += '-o -' + self.case_insensitive + 'name "' + \
                              file_pattern + '.' + ext + '" '
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
                new_path = get_user_input()
                while new_path is not '':
                    tmp_file.write(new_path)
                    new_path = get_user_input() 
                    if new_path is not '':
                        tmp_file.write('\n')
            except:
                print('Cannot open file for writing')
    

def invoke_command(self):
    """
    The final assembly and invokation of the command happens here
    """ 
    for path in self.paths:
        command='find "' + path + '" ' + self.find_arg 
        
        if self.args.grep:
            command += ' -type f '
            if not '-size' in command:
                # If `grep` is used, ensure that a file '-size' limit is set. This 
                # prevents that time is wasted for a pattern search in big files 
                # that are often compressed or encrypted archives.
                command += self.grep_file_size_threshold
            
            command += self.grep_arg 
            if not self.args.case_sensitive:
                command += '-i '
            command += '"' + self.args.grep + '"' + ' {} ' + self.grep_terminator
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
    output of the sub process while it is running. Returns 
    after the sub process exited.
    """
    process = subprocess.Popen(shlex.split(command), shell=False, stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT) # ^-- prevent command injection
    while True:
        try:
            line = process.stdout.readline().decode('utf-8')
            if process.poll() is not None and '' == line:
                break
            sys.stdout.write(line)
            sys.stdout.flush()
        except:
            sys.stderr.write('Cannot process line properly\n')


def get_user_input():
    """ python2 and 3 compatible function that gets raw user input
    """
    try: return raw_input()
    except NameError: 
        pass
    return input()

 
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
        answer = get_user_input().lower()
        if answer == '' and default_answer is not None:
            return valid_answers[default_answer]
        elif answer in valid_answers:
            return valid_answers[answer]
        else:
            print("Please respond with 'yes' or 'no'")


def main():
    search = Search()
    search.parse_arguments()
 
    if not search.args.case_sensitive:
        search.case_insensitive = 'i'
    else:
        search.case_insensitive = '' 

    # Options for `find` =============================
    # File types / names ------------------
    if search.args.file_type: 
        search.create_file_types()
        
        file_type_defs = search.find_file_type_def_or_exit() 
        if len(file_type_defs) == 1 and file_type_defs[0]['size']:
            search.find_arg += '-size ' + file_type_defs[0]['size'] + ' '
        search.add_file_ext_filter(file_type_defs, search.args.file_pattern)
    else:
        search.find_arg+='-' + search.case_insensitive + 'name "' + search.args.file_pattern + '" '
        #if search.args.regex:
        #    search.find_arg+='-regextype "posix-extended" -' + search.case_insensitive \
        #                + 'regex "' + search.args.file_pattern + '" '
        #else:
        #    search.find_arg+='-' + search.case_insensitive + 'name "' + search.args.file_pattern + '" '

    # Time --------------------------------
    if search.args.last_modified:
       search.add_time_filter() 

    # Options for `grep` =============================
    if search.args.more_context is not None:
        search.grep_arg += '--before-context=' + search.args.more_context + ' '
        search.grep_arg += '--after-context=' + search.args.more_context + ' '

    # Search path(s) =================================
    if search.args.default_path_file is not None:
        search.parse_default_paths_from_file( search.args.default_path_file ) 
    else:
        search.paths = [ search.args.search_path ]

    # Let's do it ====================================
    search.invoke_command()
         

if __name__ == '__main__':
    main()

