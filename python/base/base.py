#!/usr/bin/env python
#
# Copyright (C) 2011,2012,2014 LeZiZi Studio
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
"""
Basic Data Structure for Action, Group and Source.
"""
class Action:

    def __init__(self):
        self.inobjs = {}
        self.outobjs = {}
        self.implementation = []
        self.descriptions = [(None,"en-us")]

class Group:
    """
    Notice:
        This is the local version of the Group class, which does not
        contain other registeration information of the group.
    """
    def __init__(self):
        self.primary_id = None 
        # None for unregistered group and a hashed key for registered key in GKS protocol.
        self.local_id = None
        self.keywords = []
        self.migrated_to_id = None
        # the primary key of the target group to which this  group is migrated.

class Source:
    def __init__(self):
        self.list = []
        self.bultin_code = []
        self.bultin_obj = []

class GroupedObject:
	def __init__(self):
		self.groups = []
		self.object= None
