#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# Abstract class to represent cloudlet service
#
from abc import ABCMeta, abstractmethod, abstractproperty
class service(object):
	__metaclass__ = ABCMeta

	@abstractproperty
	def host(self):
		pass
	@abstractproperty
	def minport(self):
		pass
	@abstractproperty
	def maxport(self):
		pass
	@abstractproperty
	def description(self):
		pass
	@abstractmethod
	def getportrange(self):
		pass
	@abstractmethod
	def gethost(self):
		pass
	@abstractmethod
	def getdescription(self):
		pass
	@abstractmethod
	def handle(self):
		pass
