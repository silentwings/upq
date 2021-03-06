# This file is part of the "upq" program used on springfiles.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Daniel Troeder (daniel #at# admin-box #dot# com)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import ConfigParser
import os, os.path


class UpqConfig():
	__shared_state = {}
	paths  = {}
	jobs   = {}
	db	 = {}
	config_log = "Log replay from config parsing:\n"
	config = ""
	configfile = "upq.cfg"
	logfile = ""

	def setstr(self,obj, section, value, default):
		try:
			obj[value]=self.config.get(section, value)
		except:
			if default!=None:
				obj[value]=default
	def setpath(self, obj, section, value, default, directory=True):
		try:
			obj[value]=os.path.abspath(self.config.get(section, value))
		except:
			if default!=None:
				self.setstr(obj, section, value, os.path.abspath(default))
		if directory and not os.path.exists(obj[value]):
			os.mkdir(obj[value])
			self.conf_log("created '%s' because it didn't exist." % (obj[value]))

	def setbool(self,obj, section, value, default):
		try:
			obj[value]=self.config.getboolean(section, value)
		except:
			if default!=None:
				obj[value]=default
	def setint(self,obj, section, value, default):
		try:
			obj[value]=self.config.getint(section, value)
		except:
			if default!=None:
				obj[value]=default

	def __init__(self, configfile="", logfile=""):
		self.__dict__ = self.__shared_state
		if len(configfile)>0:
			self.configfile=configfile
		if len(logfile)>0:
			self.logfile=logfile

	def conf_log(self, msg):
		self.config_log += msg+"\n"

	def readConfig(self):
		if not os.access(self.configfile, os.R_OK):
			print >> sys.stderr, "Cannot read config file \"%s\"."%self.configfile
			sys.exit(1)
		try:
			self.config = ConfigParser.RawConfigParser()
			self.config.read(self.configfile)
		except Exception as e:
			print >> sys.stderr, "Couldn't parse %s %s" % (self.configfile, e)
			sys.exit(1)
		self.logging = {}
		self.setstr(self.logging,"logging", "loglevel", "info")
		self.setstr(self.logging,"logging", "logformat", "%(asctime)s %(levelname)-8s %(name)s.%(module)s.%(funcName)s() l.%(lineno)03d : %(message)s")
		self.setstr(self.logging,"logging", "logfile", "/var/log/upq.log")

		self.daemon = {}
		self.setbool(self.daemon, "daemon", "detach_process", False)
		self.setint(self.daemon, "daemon", "umask", 22)
		self.setstr(self.daemon, "daemon", "pidfile", None)
		self.setstr(self.daemon, "daemon", "chroot_directory", None)
		self.setint(self.daemon, "daemon", "uid", None)
		self.setint(self.daemon, "daemon", "gid", None)

		self.paths = {}
		self.setpath(self.paths, "paths", "jobs_dir", "jobs")
		self.setpath(self.paths, "paths", "socket", "/var/run/upq-incoming.sock", False)

		self.setpath(self.paths, "paths", "uploads", "uploads")
		self.setpath(self.paths, "paths", "files", "files")
		self.setpath(self.paths, "paths", "metadata", "metadata")
		self.setpath(self.paths, "paths", "broken", "paths")
		self.setpath(self.paths, "paths", "tmp", "tmp")

		self.setint(self.paths, "paths", "socket_chmod", 660)

		self.db = {}
		self.setstr(self.db, "db", "url", "sqlite:///var/lib/upq/upq.db")
		self.setbool(self.db, "db", "debug", False)

		for section in self.config.sections():
			if section.startswith("job"):
				job=section.split()[1]
				if self.config.getboolean(section, "enabled"):
					self.jobs[job]={} #initialize default values
					self.jobs[job]['concurrent']=1
					self.jobs[job]['notify_fail']=""
					self.jobs[job]['notify_success']=""
					for name, value in self.config.items(section):
						if name=="concurrent":
							self.jobs[job]['concurrent'] = self.config.getint(section, "concurrent")
						elif name=="subjobs":
							subjobs=value.strip().split(" ")
							subjobs.reverse()
							self.jobs[job]['subjobs'] = subjobs
						else:
							self.jobs[job][name]=value

				else:
					self.conf_log("   job '%s' is disabled" % job )

		self.conf_log("paths='%s'" % self.paths)
		self.conf_log("jobs:'%s'" % sorted(self.jobs.keys()))
		for job in sorted(self.jobs.keys()):
			self.conf_log("  {0}: {1}".format(job, self.jobs[job]))
		self.conf_log("db='%s'" % self.db)
		self.conf_log("daemon='%s'" % self.daemon)
