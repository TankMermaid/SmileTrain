import unittest, tempfile, subprocess, os, shutil
from SmileTrain import util, remove_primers, derep_fulllength, check_fastq_format, convert_fastq, map_barcodes, derep_fulllength, uc2otus, index
from SmileTrain.tools import check_barcodes
from SmileTrain.test import fake_fh
from Bio import SeqIO

class TestCountBarcodes(unittest.TestCase):
    '''tests for function count_barcodes'''
    def setUp(self):
        self.barcode_map = {'AAA': 'sampleA', 'TTT': 'sampleT', 'CCC': 'sampleC'}
        self.fastq = fake_fh(['@lol#AAA/1', 'CAT', '+', 'aaa', '@hoo#TTT/1', 'CAT', '+', 'aaa', '@crap#ACT/1', 'CAT', '+', 'aaa'])
    
    def test_correct(self):
        '''should count up barcodes correctly'''
        counts = check_barcodes.count_barcodes(self.fastq, self.barcode_map, max_entries=100)
        self.assertEqual(counts, {'total': 3, 'mapped': 2, 'sampleA': 1, 'sampleT': 1, 'sampleC': 0})


if __name__ == '__main__':
    unittest.main(verbosity=2)
