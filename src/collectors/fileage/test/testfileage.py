#!/usr/bin/python
# coding=utf-8
################################################################################
import os
from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import Mock
from mock import patch
from tempfile import NamedTemporaryFile

from diamond.collector import Collector
from fileage import FileAgeCollector

################################################################################

class TestFileAgeCollector(CollectorTestCase):

    def setUp(self):
        self.TEMP_FILE1 = self.create_temp_file_name()
        self.TEMP_FILE2 = self.create_temp_file_name()
        config = get_collector_config('FileAgeCollector', {
            'paths': self.TEMP_FILE1 + os.pathsep + self.TEMP_FILE2,
        })

        self.collector = FileAgeCollector(config, None)

    def test_import(self):
        self.assertTrue(FileAgeCollector)

    @patch.object(Collector, 'publish')
    def test(self, publish_mock):
        self.collector.collect()

        metrics = {
            self.collector.get_metric_key(self.TEMP_FILE1): self.collector.file_age_in_seconds(self.TEMP_FILE1),
            self.collector.get_metric_key(self.TEMP_FILE2): self.collector.file_age_in_seconds(self.TEMP_FILE2),
        }

        #self.setDocExample(collector=self.collector.__class__.__name__,
        #    metrics=metrics,
        #    defaultpath=self.collector.config['path'])
        self.assertPublishedMany(publish_mock, metrics)

    def tearDown(self):
        os.remove(self.TEMP_FILE1)
        os.remove(self.TEMP_FILE2)

    def create_temp_file_name(self):
        with NamedTemporaryFile(delete=False) as f:
            return f.name

################################################################################
if __name__ == "__main__":
    unittest.main()