#!/usr/bin/env python

"""
Module to generate test metadata
"""
import argparse
import fnmatch
import json
import logging
import os


def setup_logger():
    """
    Setup logger, set log level to debug
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(funcName)s %(message)s',
                        level=logging.DEBUG)


def parse_args():
    """
    Parse arguments from command line
    """
    parser = argparse.ArgumentParser(description='Generate test metadata')
    parser.add_argument('-i', '--input', default='.', help="Folder contains tests, default to .")
    parser.add_argument('-o', '--output', default='xen-dom0-tests-metadata.json',
                        help="output metadata file name, default to xen-dom0-tests-metadata.json")
    parser.add_argument('-s', '--skip', default=[], action='append', help="Test cases want skip")
    return parser.parse_args()


def find_tests(test_folder):
    """
    Find all test cases in a given test_folder
    """
    def is_file_executable(file):
        return os.access(file, os.X_OK)

    test_pattern = r"test[-_]*"
    test_cases = []
    # path, folders, files
    for path, _, files in os.walk(test_folder):
        pat_files = [file for file in files if fnmatch.fnmatchcase(file, test_pattern)]
        # Files with specific pattern is taken as sub-test if it is executable
        sub_tests = [file for file in pat_files if is_file_executable(os.path.join(path, file))]
        test_cases = sub_tests + test_cases

    logging.debug("Found tests %s", test_cases)
    return test_cases


def filter_tests(test_cases, skip):
    """
    Filter out tests in skip
    """
    return [t for t in test_cases if t not in skip]


def build_metadata(test_cases):
    """
    Build the whole metadata
    """
    return {
        "tests": test_cases,
    }


def save_metadata(data, output_file_name):
    """
    Persist metadata to a target file
    """
    with open(output_file_name, 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    setup_logger()
    args = parse_args()
    tests = [os.path.basename(test) for test in find_tests(args.input)]
    tests = filter_tests(tests, args.skip)
    metadata = build_metadata(tests)
    save_metadata(metadata, args.output)
    logging.info("Generate test metadata: %s", metadata)
