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

class SourceHandler():
    '''
    Provides basic source handling.

    Property:
        source: source object
    '''
    from base import Source

    def __init__(self, source=None):
        if source is None:
            self.source = self.Source()
        else:
            self.source = source

    def append(self,action):
        '''
        Append an Action to current source.
        
        Argument:
            action: An Action.
        Return:
            Boolean. True for success and False when action exsisits.
        '''
        
        self.source.list.append(action)
        
    def delete(self,act):
        '''
        Argument:
            act: An Action OR a string of action key.
        Return:
            Boolean. True for success.
        '''
        if self.source.list.count(act) == 0:
            del(self.list[self.list.index(act)])
            return(True)
        else:
            return(False)
            
    def join(self, source):
        '''
        Copy source form another souce to current source.
        '''
        for each in source:
            if self.list.count(each) == 0 :
                self.list.append(each)

    def match(self,ingroups=[],outgroups=[],implementation=None,key=None):
        ### NOT YET IMP ##
        pass

def test():
    from base import Action
    b = Action()
    b.key = "1"
    c = Action()
    c.key = "1"
    print(cmp(b,c))
    
    a = SourceHandler()
    
    print(a.append(b))
    print(a.append(c))
    print(a.source.list)
    print(a.delete(b))
    #for each in dir(a):
     #   print(getattr(a,each))
     
# test()
