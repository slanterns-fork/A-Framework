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
from source import SourceHandler

class SBCHandler(SourceHandler):
    """
    SBCHandler is a SouceHandler which is used to generate or load the
    Souce Byte-Code.

    Property:
        info: return info of Interpreter
        fatal_error: true if fatal error has occoured
        options: a list which contains some switches
        source: handling Source object
    """
    def __init__(self, source=None ,options = {}):

        if source is None:
            self.source = self.Source()
        else:
            self.source = source
        
        self.options = options
        self.info = []
        self.fatal_error = False
