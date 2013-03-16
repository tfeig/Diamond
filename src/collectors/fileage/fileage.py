# coding=utf-8

"""
Collect file age

"""

import diamond.collector
import diamond.convertor
import time
import os
import stat

class FileAgeCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(FileAgeCollector, self).get_default_config_help()
        config_help.update({
            'paths': "A %s separated list of files or directory to monitor." % os.pathsep,
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(FileAgeCollector, self).get_default_config()
        config.update({
            'enabled':  'False',
        })
        return config

    def collect(self):
        metrics = {}
        paths = self.config['paths']

        if paths is not None:
            paths = paths.split(os.pathsep)
            metrics = {}

            for path in paths:
                if os.path.exists(path):
                    metrics[self.get_metric_key(path)] = self.file_age_in_seconds(path)

            for key in metrics:
                self.publish(key, metrics[key])


    def file_age_in_seconds(self, path):
        return time.time() - os.stat(path)[stat.ST_MTIME]

    def get_metric_key(self, path):
        key = 'fileage'
        if path.startswith('/'):
            key += path
        else:
            key += '.' + path
        return key.replace('/', '.')