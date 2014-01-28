#!/usr/bin/env python
#
# Copyright (C) 2014 LeZiZi Studio
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import AFConnector
class GroupedObjectSerizer():
	from base import Group,GroupedObject
	pattern = {}
	packet = None
	def __init__(self,grp_obj_lst=[],pattern=None):
		self.objects = grp_obj_list
		self.pattern = pattern
	def dump(self):
		return packet
	def pattern(self):
		pass
	def load(self,text):
		pass
	def check(self):
		pass
