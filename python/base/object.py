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
class GroupedObjectHandler():
	from base import Group,GroupedObject
	objects = []
	def __init__(self,grp_obj_lst=None):
		if (isinstance(grp_obj_lst,list)):
			self.objects = grp_obj_list
	def add (self,grps,objs):
		if not(isinstance(objs,list)):
			objs = [objs]
		if not(isinstance(grps,list)):
			grps = [grps]
		for each in grps:
			if not(isinstance(each,self.Group)):
				raise ValueError("argument grps,objs; but a non-group thing found.")
		for obj in objs:
			temp=self.GroupedObject()
			temp.groups=grps
			temp.object=obj
			objects.append(temp)
