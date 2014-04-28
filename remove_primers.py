#!/usr/bin/env python

'''
Script that removes primers from reads in fastq files.

With a primer
    AAAAA

entries like
    @lolapolooza
    TAAAACATCATCATCAT
    +whatever
    abcdefghijklmnopq

become entries like
    @lolapolooza
    CATCATCATCAT
    +
    fghijklmnopq
'''

import argparse, itertools, sys
import util
#from util import *

class PrimerRemover():
    def __init__(self, fastq, primer, max_primer_diffs, output_type='string'):
        '''
        Remove well-matched primers from sequences in a fastq file

        Parameters
        fastq : sequence or iterator of strings
            lines in the fastq file
        primer : string
            the primer sequence to be removed
        max_primer_diffs : int
            the maximum number of mismatches allowed before throwing out the read
        output_type : string 'string' or 'list' (default 'string')
            output format for iterator. string is a single string; list is the 3-element list
        '''

        self.fastq_iterator = util.fastq_iterator(fastq)
        self.primer = primer
        self.primer_length = len(self.primer)
        self.max_primer_diffs = max_primer_diffs

        self.output_type = output_type
        
        self.n_successes = 0
        self.n_failures = 0

    def __iter__(self):
        return self

    def next(self):
        '''iterator over successfully trimmed input fastq entries'''

        while True:
            [at_line, seq_line, quality_line] = self.fastq_iterator.next()

            # find the best primer position in the sequence
            primer_start_index, n_primer_diffs = util.mismatches(seq_line, self.primer, 15)

            # if we find a good match, trim the sequence and the
            # quality line and yield a single string
            if n_primer_diffs <= self.max_primer_diffs:
                primer_end_index = primer_start_index + self.primer_length
                trimmed_seq = seq_line[primer_end_index:]
                trimmed_quality = quality_line[primer_end_index:]
                self.n_successes += 1

                if self.output_type == 'string':
                    return "\n".join([at_line, trimmed_seq, '+', trimmed_quality])
                elif self.output_type == 'list':
                    return [at_line, trimmed_seq, trimmed_quality]
            else:
                self.n_failures += 1

    def print_entries(self):
        '''print the successfully trimmed entries'''

        timer = util.timer()
        for entry in self:
            print entry
        self.elapsed_time = timer.next()

    def diagnostic_message(self):
        '''return a string about how the trimming went'''
        return "Primer removal:\n%s successes and %s failures (?? failure rate)\n%f seconds elapsed\n" %(self.n_successes, self.n_failures, self.elapsed_time)


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('fastq', help='input fastq file')
    parser.add_argument('primer', help='primer sequence')
    parser.add_argument('-m', '--max_primer_diffs', default=0, type=int, help='maximum number of nucleotide mismatches in the primer (default: 0)')
    parser.add_argument('-l', '--log', default=None, type=str, help='log file for successes, failures, and time elapsed')
    args = parser.parse_args()

    r = PrimerRemover(open(args.fastq), args.primer, args.max_primer_diffs)
    r.print_entries()

    if args.log is not None:
        with open(args.log, 'w') as f:
            f.write(r.diagnostic_message())
