import argparse

# setup argparse
parser = argparse.ArgumentParser()
parser.add_argument('path', help="the path of the drive or directory to perform the operation on", type=str)
args = parser.parse_args()

source_path = args.path