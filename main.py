import argparse
import sys
from pathlib import Path
import time
import colorama
from colorama import Fore, Back, Style
from hashlib import sha256

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
        print(Style.BRIGHT + Fore.GREEN + 'Starting clean...' + Style.RESET_ALL + Fore.RESET)
        print()
    
    def create_log_file(self):
        try:
            if self.log_path.exists:
                self.log_path.unlink()
            self.log_path.touch()
            self.verbose(f'Created log file at {str(self.log_path)}.')
        except FileNotFoundError:
            self.warning('Failed to create log file.')
    
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
