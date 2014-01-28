#!/usr/bin/env python
# -*- coding: utf-8 -*-  
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

import AFConnector,io
class AOSwriter():
	import cPickle as pickle
	def __init__(self):
		print ("DB bootup.")
		self.data = io.open( AFConnector.connector_get_file("aos-data"), "a")
		self.opt_counter = 0
		try:
			mem_indx_dump = open(AFConnector.connector_get_file("aos-index-mem"),"r")
			self.mem_indx = self.pickle.load(mem_indx_dump)
			mem_indx_dump.close()
		except Exception:
			self.mem_indx = {}
	def dump_mem_index(self):
		mem_indx_dump = open(AFConnector.connector_get_file("aos-index-mem"),"w")
		self.pickle.dump(self.mem_indx,mem_indx_dump,True)
		mem_indx_dump.close()

	def __del__(self):
		print ("DB Operation:"+str(self.opt_counter))
		print ("DB mem-index serize.")
		
		self.dump_mem_index()
		self.merge_index()
		print ("DB shutdown.")
		self.data.close()
		
	def merge_index(self):
		print ("DB index merge.")
		self.indx = io.open( AFConnector.connector_get_file("aos-index"), "w")
		sorted_new = sorted( self.mem_indx.items() ) 
		for each in sorted_new:
			self.indx.write(each[0].replace(u",",u""))
			for pos in each[1]:
				self.indx.write (u","+unicode(hex(pos)[2:]))
			self.indx.write(u"\n")
		self.indx.close()
		
	def get_entities_num(self,key):
		if not(key in self.mem_indx):
			return 0
		else:
			return len(self.mem_indx[key])
			
	def insert (self,entity_type,key,packet):
		data_pos = self.data.tell()
		self.data.write('{"'+entity_type+'":'+packet+'}\n')
		if not(key in self.mem_indx):
			self.mem_indx[key] = []
		self.mem_indx[key].append(data_pos)
		self.opt_counter +=1
		if (self.opt_counter % 100000==1):
			self.merge_index()
			self.dump_mem_index()
