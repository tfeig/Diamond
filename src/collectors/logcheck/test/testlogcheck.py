#!/usr/bin/python
# coding=utf-8
################################################################################

from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import patch

from diamond.collector import Collector
from logcheck import LogCheckCollector
import os

################################################################################


class TestLogCheckCollector(CollectorTestCase):

    def test_import(self):
        self.assertTrue(LogCheckCollector)

    def test_should_find_0_occurences_in_1st_run(self):
        """
        logfile_path = str(self.getFixturePath('logfile_1st_run.log'))
        seekfile_path = logfile_path.replace('logfile_1st_run.log', 'logfile_1st_run.seek')
        config = get_collector_config('LogCheckCollector', {
            'interval': 10,
            'pattern': ' ERROR ',
            'logfile':  logfile_path,
            'seekfile': seekfile_path
        })
        self.collector = LogCheckCollector(config, None)

        self.collector.collect()

        metrics = {
            'occurrences':  0
        }

        self.setDocExample(collector=self.collector.__class__.__name__,
                           metrics=metrics,
                           defaultpath=self.collector.config['path'])
        self.assertPublishedMany(publish_mock, metrics)

        # clean up
        os.remove(seekfile_path);
        """
        self.internal_test('1st', 0, False)

    def test_should_find_3_occurrences_in_2nd_run(self):
        self.internal_test('2nd', 3, True)

    def test_should_find_0_occurrences_in_3rd_run(self):
        self.internal_test('3rd', 0, True)

    def test_should_find_0_occurrences_after_log_was_rolled(self):
        self.internal_test('4th', 0, True)

    @patch.object(Collector, 'publish')
    def internal_test(self, run, occurrences, seekfileExists, publish_mock):
        logfile_path = str(self.getFixturePath('logfile_' + run + '_run.txt'))
        seekfile_path = logfile_path.replace('logfile_' + run + '_run.txt', 'logfile_' + run + '_run.seek')

        if seekfileExists:
            # save current seekvalue for later clean up (collector will change seek file)
            seekfile = open(seekfile_path, 'r')
            seekpos = seekfile.readline()
            seekfile.close()

        config = get_collector_config('LogCheckCollector', {
            'interval': 10,
            'pattern': ' ERROR ',
            'logfile':  logfile_path,
            'seekfile': seekfile_path
        })
        self.collector = LogCheckCollector(config, None)

        self.collector.collect()

        metrics = {
            'occurrences':  occurrences
        }

        self.setDocExample(collector=self.collector.__class__.__name__,
                           metrics=metrics,
                           defaultpath=self.collector.config['path'])
        self.assertPublishedMany(publish_mock, metrics)

        # clean up
        if seekfileExists:
            #restore old seek value
            seekfile = open(seekfile_path, 'w')
            seekfile.write(seekpos)
        else:
            #remove seek file
            os.remove(seekfile_path)


################################################################################
if __name__ == "__main__":
    unittest.main()
