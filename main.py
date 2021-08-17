import argparse
import sys
from pathlib import Path
import time
import colorama
from colorama import Fore, Back, Style
from hashlib import sha256
import glob

colorama.init()

class DuplicateRemover:

    def __init__(self, source_path: str, no_inputs = False, generate_logs = False, log_path = None, verbose = False):
        # log_path stuff
        log_path_set = True if log_path else False
        if not log_path:
            log_path = 'log.txt'
        
        # setup source_path and log_path
        log_path_obj = Path.cwd() / log_path
        log_path_obj = log_path_obj.resolve()
        source_path_obj = Path(source_path).resolve()

        # validate source path
        if not source_path_obj.is_dir():
            self.error(f"Path '{Style.BRIGHT + str(source_path_obj) + Style.RESET_ALL}' is not a valid directory.")
            sys.exit()

        # properties
        self.source_path = source_path_obj
        self.hashes = {}
        self.num_of_duplicates = 0
        self.num_scanned = 0

        ## config properties
        self.no_inputs = no_inputs
        self.generate_logs = generate_logs
        self.log_path = log_path_obj
        self.log_path_set = log_path_set
        self.is_verbose = verbose
    
    def verbose(self, *args, **kwargs):
        if self.is_verbose:
            print(f'{Fore.CYAN}{Style.DIM}[VERBOSE]{Fore.RESET}', *args, Style.RESET_ALL, **kwargs)
    
    def warning(self, *args, **kwargs):
        print(f'{Fore.YELLOW}{Style.BRIGHT}[WARNING]{Fore.RESET}{Style.RESET_ALL}', *args, **kwargs)
    
    def error(self, *args, **kwargs):
        print(f'{Fore.RED}{Style.BRIGHT}[ERROR]{Fore.RESET}{Style.RESET_ALL}', *args, **kwargs)

    def welcome(self):
        print()
        print('***********************************')
        print(f'***      {Fore.BLUE}DUPLICATE REMOVER{Fore.RESET}      ***')
        print('***********************************')
        print()
        print(f"RECURSIVE CLEAN ON PATH: {Style.BRIGHT + str(self.source_path) + Style.RESET_ALL}")

        if not self.no_inputs:
            while True:
                print()
                answer = str.lower(input('Perform recursive clean? (Y/n):'))
                if answer == 'y':
                    break
                elif answer == 'n':
                    print('Exiting...')
                    sys.exit()
                else:
                    print('Invalid option.')

        print()
        if self.generate_logs:
                if self.log_path_set or self.is_verbose:
                    print(f"Log file location: {Style.BRIGHT + str(self.log_path) + Style.RESET_ALL}")
                else:
                    print(f"Log file location: {Style.BRIGHT + self.log_path.name + Style.RESET_ALL}")
        print(Style.BRIGHT + Fore.GREEN + 'Starting clean... (this may take a while)' + Style.RESET_ALL + Fore.RESET)
        print()

    def log(self, *args):
        try:
            with self.log_path.open('a') as log_file:
                for line in args:
                    log_file.writelines(line + '\n')
        except:
            self.error('Failed to write to log.')
    
    def create_log_file(self):
        try:
            if self.log_path.exists:
                self.log_path.unlink()
            self.log_path.touch()
            self.verbose(f'Created log file at {str(self.log_path)}.')

            self.log('Duplicates:')
        except FileNotFoundError:
            self.error('Failed to create log file.')
            sys.exit()
    
    def hash(self, filepath):
        filehash = sha256()
        try:
            with filepath.open('rb') as f:
                fileblock = f.read(65536)
                while len(fileblock) > 0:
                    filehash.update(fileblock)
                    fileblock = f.read(65536)
                filehash = filehash.hexdigest()
            return filehash
        except:
            return False
    
    def clean(self):
        self.verbose('Getting all filepaths recursively...')
        all_paths = sorted(self.source_path.glob('**/*'))
        self.verbose('Completed.')

        self.verbose('Marking directories...')
        filepaths = []
        for path in all_paths:
            if path.is_file():
                filepaths.append(path)
        self.verbose('Done.')

        num_of_files = len(filepaths)

        for index, filepath in enumerate(filepaths):
            self.verbose(f'Scanning path {str(index)} of {str(num_of_files)}.')
            if filepath.is_dir():
                self.verbose(f'Path is a directory. Skipping...')
                continue
            hash = self.hash(filepath)
            
            if hash in self.hashes.keys():
                # file is a duplicate, handle as such
                self.verbose(f'File {str(filepath)} is a duplicate of {self.hashes[hash]}. Removing.')
                try:
                    filepath.unlink()
                    self.num_of_duplicates += 1
                    self.log(f'"{str(filepath)}" is a duplicate of "{self.hashes[hash]}"')
                except:
                    self.error(f'Failed to remove {Style.BRIGHT}{filepath}{Style.RESET_ALL}')
            else:
                self.hashes[hash] = str(filepath)
            self.num_scanned += 1

        print(Fore.GREEN + 'Scan completed.' + Fore.RESET)
        print('Number of files scanned:', Fore.CYAN + str(self.num_scanned) + Fore.RESET)
        print('Number of duplicates:', Fore.RED + str(self.num_of_duplicates) + Fore.RESET)
    
if __name__ == '__main__':
    # setup argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="the path of the drive or directory to perform the operation on", type=str)
    parser.add_argument('-n', '--no-inputs', help="skips all inputs, assuming the default value", action='store_true')
    parser.add_argument('-q', '--quiet', help="the app will not generate log files", action="store_true")
    parser.add_argument('-o', '--output', help="the path of the log output file", type=str)
    parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    args = parser.parse_args()

    source_path = args.path
    
    # run app
    App = DuplicateRemover(
        source_path,
        no_inputs=args.no_inputs,
        generate_logs=(not args.quiet),
        log_path=args.output,
        verbose=args.verbose)
    App.welcome()
    App.create_log_file()
    App.clean()
