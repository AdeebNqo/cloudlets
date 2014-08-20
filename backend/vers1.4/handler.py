#
#
# Copyright 2014 Zola Mahlaza <adeebnqo@gmail.com>
# This class handles communication between the services
# and the broker
#
# "If builders built buildings the way programmers wrote programs, then
#  the first woodpecker that came along wound destroy civilization."
# -Gerald Weinberg
class handler(object):
	def __init__(self):
		self.serviceman = servicemanager()
