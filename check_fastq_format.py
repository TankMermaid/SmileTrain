#!/usr/bin/env python

'''
Before running any steps in the pipeline, check your data to see if the fastq input is in
Illumina 1.3-1.7 format, specificially that
    * the @ line follows the format @stuff:with:colons#BARCODE/1 (or /2 for reverse reads)
    * the quality line uses Sanger encoding (ascii offset 64, high score h to low score B)
'''

import itertools, os, os.path, sys, argparse, shutil
import util

def check_illumina_format(ifilenames, itargets):
    '''
    Raise error if any of the input filenames are not in the desired format.
    
    filenames : string, or iterable of strings
        files to be checked
    target : string, or iterable of strings
        'illumina13' or 'illumina18' or 'ambiguous', or some combination
    '''
    
    # convert to lists if required
    if type(ifilenames) is str:
        filenames = [ifilenames]
    else:
        filenames = ifilenames
    
    if type(itargets) is str:
        targets = [itargets]
    else:
        targets = itargets
    
    # check that input targets are in acceptable list
    acceptable_targets = set(['illumina13', 'illumina18', 'ambiguous'])
    if not set(targets).issubset(acceptable_targets):
        bad_targets = targets - acceptable_targets
        raise ArgumentError("unrecognized format type(s): %s" % bad_targets)
    
    format_f = lambda fn: file_format(open(fn))
    
    # check all the formats
    formats = [file_format(open(fn)) for fn in filenames]
    tests = [form in targets for form in formats]
    bad_files = [fn for fn, test in zip(filenames, tests) if test == False]
    bad_forms = set([form for form, test in zip(formats, tests) if test == False])
    
    # complain if something went wrong
    if False in tests:
        bad_info = "\n".join([" ".join([fn, form]) for fn, form in zip(filenames, bad_forms)])
        raise RuntimeError("files do not appear to be in %s format: \n%s" % (targets, bad_info))

def file_format(fastq, max_entries=10):
    '''
    what format is the file?
    
    returns : string
        'illumina13', 'illumin18', or 'ambiguous'
    '''
    
    for i, (at_line, seq_line, qua_line) in enumerate(util.fastq_iterator(fastq)):
        if i > max_entries:
            raise RuntimeError("could not verify format after %d entries" % max_entries)
        
        # make sure we can parse the at line
        rid = util.fastq_at_line_to_id(at_line)
        
        # check the quality line's character content
        return quality_line_format(qua_line)
        
def quality_line_format(line):
    '''
    Guess the fastq format using the quality codes.
    
    line : string
        quality line from a fastq entry
        
    returns : 'illumina13', 'illumina18', 'ambiguous'
        either Illumina 1.3-1.7 (B--h), Illumina 1.8 ("--J), or ambiguous
    '''
    
    matches_illumina13 = all([c in util.illumina13_codes for c in list(line)])
    matches_illumina18 = all([c in util.illumina18_codes for c in list(line)])
    
    if matches_illumina13 and matches_illumina18:
        return 'ambiguous'
    elif matches_illumina13 and not matches_illumina18:
        return 'illumina13'
    elif matches_illumina18 and not matches_illumina13:
        return 'illumina18'
    elif not matches_illumina18 and not matches_illumina13:
        raise RuntimeError("quality line doesn't match known encoding: %s" % line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify that fastq is in Illumina 1.3-1.7 format')
    parser.add_argument('fastq', help='input fastq')
    args = parser.parse_args()
    
    with open(args.fastq) as f:
        format_guess = file_format(f)
        if format_guess == 'illumina13':
            print "Looks like Illumina 1.3-1.7 format. Proceed with the pipeline!"
        elif format_guess == 'illumina18':
            print "Looks like Illumina 1.8 format. You may need to convert. Beware..."
        elif format_guess == 'ambiguous':
            print "Could be either 1.3-1.7 or 1.8 format. Ambiguous. Proceed with caution."
        else:
            raise RuntimeError