# coding=utf-8

"""
A collector that reports the JVM memory status from jstatd.

(C) 2013 Robert Ehmann <robert.ehmann@immobilienscout24.de>
(C) 2013 Thomas Hieck <thomas.hieck@immobilienscout24.de>

#### Dependencies

 * A sane universe
 * jstatd

"""

import diamond.collector
import os

class JstatdCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        config_help = super(JstatdCollector, self).get_default_config_help()
        config_help.update({
            'vmId': 'Name of java process to monitor',
        })
        return config_help

    def get_default_config(self):
        """
        Returns the default collector settings
        """
        config = super(JstatdCollector, self).get_default_config()
        config.update({
            'path': 'jstat'
        })
        return config

    def collect(self):
        """
        Overrides the Collector.collect method
        """

        # loop through configured vmIds
        vmId = self.config['vmId']

        self.log.debug("Fetching JVM stats for process '%s'" % vmId)

        # find process id from jps
        cmd = "jps | grep " + vmId + " | cut -d' ' -f1"
        pid = os.popen(cmd).readline().rstrip()

        if not pid:
            self.log.info("JVM process '%s' not found." % vmId)
            return

        self.log.debug("JVM-PID: " + pid)

        # fetch memory maxima
        # values: NGCMN    NGCMX     NGC     S0C   S1C       EC      OGCMN      OGCMX       OGC         OC      PGCMN    PGCMX     PGC       PC     YGC    FGC
        cmd = "jstat -gccapacity " + pid + " | tail -1"
        data = os.popen(cmd).readline().rstrip()
        maxima = data.replace(',', '.').split()

        # fetch memory usage
        # values: S0C    S1C    S0U    S1U      EC       EU        OC         OU       PC     PU    YGC     YGCT    FGC    FGCT     GCT
        cmd = "jstat -gc " + pid + " | tail -1"
        data = os.popen(cmd).readline().rstrip()
        usage = data.replace(',', '.').split()

        if len(maxima) != 16:
            self.log.error("JstatdCollector: Got invalid data from jstat -gccapacity")
            return

        if len(usage) != 15:
            self.log.error("JstatdCollector: Got invalid data from jstat -gc")
            return

        # generate metrics
        perm_usage = (float(usage[9]) / float(maxima[11])) * 100
        self.publish("%s.perm_usage" % vmId, perm_usage)
        self.log.debug("Sent metric: '" + "%s.perm_usage" % vmId + "' value: " + str(perm_usage))

        heap_usage = ((float(usage[2]) + float(usage[3]) + float(usage[5]) + float(usage[7])) / \
                     (float(maxima[1]) + float(maxima[7]))) * 100
        self.publish("%s.heap_usage" % vmId, heap_usage)
        self.log.debug("Sent metric: '" + "%s.heap_usage" % vmId + "' value: " + str(heap_usage))
