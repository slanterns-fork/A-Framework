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

#from optparse import OptionParser
#def main():
#    parser = OptionParser()
#    parser.add_option("-f", "--file", dest="file", help="import code form this file", metavar="file")
#    parser.add_option("-o", "--output", dest="output", help="output source file", metavar="output")
#    parser.add_option("-v","--version",dest="version",help="specify the APL version",metavar="version")
#    (options, args) = parser.parse_args()
#    if options.file is None or options.output is None:
#        parser.print_help()
#    print (options.file)
#    print(options.output)
#    print (args)
    
from interpreter import Interpreter
from sml import SMLHandler
def main():
   
    raw_code = """
Input>>Number(num1) Integer 
        Input>>Number(num2) Integer
             num1,num2>>Number(ans) Added
             ans>>Screen(Output) Demo ConsolePlus
"""
    a = Interpreter()
    a.parser(raw_code)
    print(a.info)
    b=SMLHandler(a.source)
    b.build_dom_tree()
    print(b.info)
    ss = b.build_sml()
    print(ss)



    c=SMLHandler()
    c.read_sml(ss)
    c.read_dom_tree()


    
    c.dom = c.builder.getDOMImplementation()
    c.tree = c.dom.createDocument("http://cp-web.appspot.com/source", "Source", None)
    c.build_dom_tree()
    print(c.build_sml())
main()
