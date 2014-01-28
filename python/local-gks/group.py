#!/usr/bin/env python
#
# Copyright (C) 2012,2014 LeZiZi Studio
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
class LocalGorup():
	from base import Group
	import cPickle as pickle
	def __init__(self):
		try:
			local_group_file = open( AFConnector.connector_get_file("local-group"),"r")
			self.local_group = self.pickle.load(local_group_file)
			local_group_file.close()
		except IOError:
			self.local_group = {}
			
	def __del__(self):
		local_group_file = open( AFConnector.connector_get_file("local-group"),"w")
		self.pickle.dump(self.local_group,local_group_file,True)
		local_group_file.close()
		
	def local_register(self,grp,generate_a_local_id=False):
		local_group_transaction = self.local_group
		
		if not(isinstance(grp,self.Group)):
			raise ValueError("Group to be registered is not valid.")
		else:
			if grp.primary_id in local_group_transaction:
				raise ValueError("Group ID duplicated: Group is already registered.")
			else:
				if not(generate_a_local_id):
					current_id = grp.primary_id
				else:
					current_id=grp.primary_id[2:5]
					if not(grp.local_id in local_group_transaction):
						grp.local_id = current_id
					else:
						raise ValueError("Unable to generate a local ID!!!!")
				
				# inverse_resolution
				local_group_transaction[current_id]=grp
				if current_id != grp.primary_id:
					local_group_transaction[grp.primary_id]=grp
				# resolution
				for each in grp.keywords:
					if each in local_group_transaction:
						raise ValueError("Group keyword '"+each+"' is duplicated.")
					else:
						local_group_transaction[each]=grp
		self.local_group = local_group_transaction
		
	def resolution (self,label):
		if label in self.local_group:
			return self.local_group[label]
		else:
			return None

class GroupHandler():
	from base import Group
	import hashlib
	def __init__(self,group = None):
		self.editable = True
		if group is None:
			self.group = self.Group()
		else:
			self.group = group
			loc = LocalGorup()
			# local-registered group is not editable
			self.editable = (loc.resolution(group.primary_id)==None)
	
	def add_keyword (self,keyword):
		if (self.editable):
			if not(keyword in self.group.keywords):
				self.group.keywords.append(keyword)
		else:
			raise ValueError("Group is not editable")
	
	def set_id(self,key,make_primary=False):
		if (self.editable):
			if make_primary:
				self.group.primary_id = key
			else:
				self.group,local_id = key
		else:
			raise ValueError("Group is not editable")
	
	def register(self):
		'''
		The group will not be sent to the GKS but a local key will ba arranged
		to it so that it can be recognized in the framework.

		After the register method, the attribute 'changeable' will be False,
		and Group will be frozen just as if it were sent to the GKS system. 
		'''
		self.editable = False
		self.group.keywords = sorted(self.group.keywords)
		self.group.primary_id = self.hashlib.md5(",".join(self.group.keywords)).hexdigest()
		loc = LocalGorup()
		loc.local_register(self.group)
		
"""
#######test#######

grp = GroupHandler()
grp.add_keyword("haha")

grp.add_keyword("lezizi")
grp.register()

loc = LocalGorup()
print(loc.resolution("lezizi").primary_id)
"""
