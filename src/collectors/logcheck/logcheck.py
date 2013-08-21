# coding=utf-8

"""
Description:

This plugin will scan arbitrary text files looking for regular expression
matches.  The text file to scan is specified with config parameter 'logfile'.
'seekfile' specifies the temporary file used to store the seek byte position
of the last scan. This file will be created automatically on the first
scan. 'pattern' can be any RE pattern that python's syntax accepts.

Output:

This plugin returns a 1-entry-map, the key of which is the metric name provided in the config
and the value is the number of pattern matches in the checked log file section.

To run this collector in test mode you can invoke the diamond server with the
-r option and specify the collector path.

>  diamond -f -l -r path/to/LogCheckCollector.py -c conf/diamond.conf.example

Diamond supports dynamic addition of collectors. Its configured to scan for new
collectors on a regular interval (configured in diamond.cfg).
If diamond detects a new collector, or that a collectors module has changed
(based on the file's mtime), it will be reloaded.

Diamond looks for collectors in /usr/lib/diamond/collectors/ (on Ubuntu). By
default diamond will invoke the *collect* method every 60 seconds.

Diamond collectors that require a separate configuration file should place a
.cfg file in /etc/diamond/collectors/.
The configuration file name should match the name of the diamond collector
class.  For example, a collector called
*logcheck.LogCheckCollector* could have its configuration file placed in
/etc/diamond/collectors/LogCheckCollector.cfg.

"""

import diamond.collector
import re
import os


class LogCheckCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(LogCheckCollector, self).get_default_config_help()
        config_help.update({
            'logfile':      'path to log file to be checked',
            'seekfile':     'path to the seek file that stores the position reached in the last check',
            'pattern':      'RegEx pattern to search for',
            'metric_name':  'name of the metric to report'
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(LogCheckCollector, self).get_default_config()
        config.update({
            'path':         'logcheck',
            'logfile':      None,
            'seekfile':     None,
            'pattern':      None,
            'metric_name':  'occurrences'
        })
        return config

    def collect(self):
        # get and check config params
        logfile_path = self.config['logfile']
        seekfile_path = self.config['seekfile']
        pattern_string = self.config['pattern']
        metric_name = self.config['metric_name']

        if logfile_path is None or len(logfile_path) == 0:
            self.log.error('No logfile specified')
            return {}
        if seekfile_path is None or len(seekfile_path) == 0:
            self.log.error('No seekfile specified')
            return {}
        if pattern_string is None or len(pattern_string) == 0:
            self.log.error('No pattern specified')
            return {}
        else:
            try:
                pattern = re.compile(pattern_string)
            except re.error:
                self.log.error('Invalid pattern specified: %s' % pattern_string)
                return {}
        if metric_name is None or len(metric_name) == 0:
            self.log.error('No metric_name specified')
            return {}

        # Open log file
        try:
            logfile = open(logfile_path)
        except IOError as e:
            self.log.error('logfile %s cannot be opened: %s' % (logfile_path, e.strerror))
            return {}

        seekpos_string = '0'
        # Try to open log seek file.
        try:
            seekfile = open(seekfile_path)
            # read first (and only) line of seekfile
            seekpos_string = seekfile.readline();
            seekfile.close()
        except IOError:
            #If open fails, we seek from beginning of file by default.
            pass

        try:
            seekpos = int(seekpos_string)
            if seekpos < 0:
                raise ValueError
        except ValueError:
            self.log.warn('Illegal seekpos specified in %s: %s. Resorting to 0.' % (seekfile_path, seekpos_string))
            seekpos = 0

        #  If file is empty, no need to seek...
        if seekpos > 0:
            # Compare seek position to actual file size.
            size = os.path.getsize(logfile_path)
            # If file size is smaller then we just start from beginning i.e. file was rotated, etc.
            if seekpos <= size:
                logfile.seek(seekpos);

        # Loop through every line of log file and check for pattern matches.
        # Count the number of pattern matches
        matches = 0
        for line in logfile:
            if pattern.search(line):
                matches += 1

        # Overwrite log seek file and print the byte position we have seeked to.
        try:
            seekfile = open(seekfile_path, 'w')
            seekfile.write(str(logfile.tell()))
            seekfile.close()
        except IOError:
            self.log.error('seekfile %s cannot be opened for writing: %s' % (logfile_path, e.strerror))
            return {}

        # Close the log file.
        logfile.close()

        # Publish Metric
        self.publish(metric_name, matches)
