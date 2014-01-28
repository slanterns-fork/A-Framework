#!/usr/bin/env python
#
# Copyright (C) 2012 LeZiZi Studio
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
import ConfigParser
def connector_get_conf_path():
	import os
	path = os.getcwd()
	while len(path)>0:
		if os.path.exists(path+"/AFConnector.conf"):
			return path
		path=path[0:path.rfind("/")]
		
def connector_import_package(name):
    import sys
    cf = ConfigParser.ConfigParser() 
    cf.read(connector_get_conf_path()+"/AFConnector.conf")
    ret = cf.get("python_packages", name)
    sys.path.append(connector_get_conf_path()+ret)

def connector_get_file(name):
	cf = ConfigParser.ConfigParser() 
	cf.read(connector_get_conf_path()+"/AFConnector.conf")
	name = cf.get("local_file", name)	
	if (name.find('*')>=0):
		return name.replace('*','')
	else:
		return connector_get_conf_path()+name

def main():
	try:
		connector_import_package("base")
	except Exception:
		raise ValueError("AFConnector.conf not found.") 
main()
