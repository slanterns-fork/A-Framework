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

import AFConnector
class ActionHandler():
    from base import Action,Group
    '''
    Property:
        action: action being processed
        key: the key for this action used locally
    '''
    
    def __init__(self, action = None):
        if action is None:
            self.action = self.Action()
        else:
            self.action = action
        self.key = None
        
    def add_in_obj(self,objid):
        if objid in self.action.inobjs:
            raise ValueError("IN Object duplicated. (Two abstract Objects may have the same name: "+objid+".)")
        else:
            self.action.inobjs[objid]=[]
    
    def add_out_obj(self,objid):
        if objid in self.action.outobjs:
            raise ValueError("OUT Object duplicated. (Two abstract Objects may have the same name: "+objid+".)")
        else:
            self.action.outobjs[objid]=[]
    
    def add_in_group(self,objid,group):
        if objid in self.action.inobjs.keys():
            if not isinstance(group,self.Group):
                raise ValueError("INNER ERROR (Argument group is not a Group.)")
            self.action.inobjs[objid].append(group)
            self.hash()
        else:
            raise ValueError("INNER ERROR, IN Object excess of authority. (The name "+objid+" of an IN Object may be used before define.)")

    def add_out_group(self,objid,group):
        if objid in self.action.outobjs.keys():
            if not isinstance(group,self.Group):
                raise ValueError("INNER ERROR (Argument group is not a Group.)")
            self.action.outobjs[objid].append(group)
            self.hash()
        else:
            raise ValueError("INNER ERROR, OUT Object excess of authority. (The name "+objid+" of an OUT Object may be used before define.)")
        
    def add_implementation(self,action):
        self.action.implementation.append(action)
        self.hash()
        
    def hash(self):
        '''
        Assign an UUDI as Action Handler key.
        
        Retrun:
            UUID based key for action.
        '''
        ##### GuidGenerator #####
        import uuid
        if self.key is None:
            self.key = uuid.uuid1()
        return(self.key)
