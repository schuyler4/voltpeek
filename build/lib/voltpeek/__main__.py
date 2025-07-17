#!/usr/bin/python3

from voltpeek.interface import UserInterface

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

def main():
    user_scope_interface = UserInterface(debug=args.debug)
    user_scope_interface()

if __name__ == '__main__':
    main()