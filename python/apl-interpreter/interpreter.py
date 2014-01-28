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
class Interpreter(SourceHandler):
    '''
    APL interpreter is a SouceHandler which is used to interpret the code
    in Strict APL.

    Property:
        info: return info of Interpreter
        fatal_error: true if fatal error has occoured
        options: a list which contains some switches
        source: generated Source object
    '''

    from action import ActionHandler
    from group import GroupHandler
    
    def __init__(self, source=None ,options = {}):
        if source is None:
            self.source = self.Source()
        else:
            self.source = source
        
        self.options = options
        self.info = []
        self.fatal_error = False
        
    def reg_group(self,expr):
        """
        Return (None,Grp) when it is a common Group, and a (Obj,Grp) for a GroupArg.
        """
        temp_group_handler = self.GroupHandler()
        if expr.find(":")>=0:
            temp_group_handler.new(expr[0:expr.find(":")])
            temp_group_handler.register()
            return (expr[expr.find(":")+1:len(expr)],temp_group_handler.group)
        else:
            temp_group_handler.register()
            temp_group_handler.new(expr)
            return (None,temp_group_handler.group)
        
    def expr(self,expr):
        """
        Arguments:
            expr: a line of Strict APL expression
        
        Return:
            action: an Action object.
        """
        if expr is not None and expr.find(">>")<>-1:
            a = self.ActionHandler()
            # split at ">>"   
            left = expr[0:expr.find(">>")].split(",")
            right = expr[expr.find(">>")+2:len(expr)].split(",")
            try:
                for i in range(len(left)):
                    left_obj = None
                    # split again with space
                    for each in left[i].split(" "):
                        if len(each)>=1 :
                            if left_obj==None:
                                # deal with the first word, which is the descriptor of Object
                                if each.find("(")<>-1:
                                    # New Object
                                    left_obj = each[each.find("(")+1:each.find(")")].replace(" ","")
                                    a.add_in_obj(left_obj)

                                    # "OBJModel(...)" is a syntactic sugar for Group
                                    GroupArg = self.reg_group(each[0:each.find("(")])
                                    a.add_in_group(left_obj,GroupArg[1])
                                else:
                                    # New Object
                                    left_obj = each
                                    a.add_in_obj(left_obj)
                            else:
                                # deal with other words, which are the descriptor of Groups
                                GroupArg = self.reg_group(each)
                                # GroupArg is a syntactic sugar for a Group and an Object
                                if GroupArg[0] is not None:
                                    a.add_in_obj(GroupArg[0])
                                    a.add_in_group(GroupArg[0],GroupArg[1])
                                else:
                                    a.add_in_group(left_obj,GroupArg[1])
                                
            except ValueError,e:
                self.info.append('<Error> Fail to parser the left expression("'+expr[0:expr.find(">>")]+'"): '+str(e))
                fatal_error=True
                return(None)
            try:
                for i in range(len(right)):
                    right_obj = None
                    # split again with space
                    for each in right[i].split(" "):
                        if len(each.replace(" ",""))>=1 :
                            if right_obj==None:
                                # deal with the first word, which is the descriptor of Object
                                if each.find("(")<>-1:
                                    # New Object
                                    right_obj = each[each.find("(")+1:each.find(")")].replace(" ","")
                                    a.add_out_obj(right_obj)

                                    # "OBJModel(...)" is a syntactic sugar for Group
                                    GroupArg = self.reg_group(each[0:each.find("(")])
                                    a.add_out_group(right_obj, GroupArg[1])
                                else:
                                    # New Object
                                    right_obj = each
                                    a.add_out_obj(right_obj)
                            else:
                                # deal with other words, which are the descriptor of Groups
                                GroupArg = self.reg_group(each)
                                # GroupArg is a syntactic sugar for a Group and an Object
                                if GroupArg[0] is not None:
                                    a.add_in_obj(GroupArg[0])
                                    a.add_in_group(GroupArg[0],GroupArg[1])
                                    # Notice that here it is processing OUT group, but GroupArg is
                                    # sitll for IN object.
                                else:
                                    a.add_out_group(right_obj,GroupArg[1])
            except ValueError,e:
                self.info.append('<Error> Fail to parser the right expression("'+expr[expr.find(">>")+2:len(expr)]+'"): '+str(e))
                fatal_error = True
                return (None)
            if (left_obj is None) or (right_obj is None):
                # Fail to construct
                del a
                self.info.append('<Error> Broken expression("'+expr+'").')
                fatal_error = True
                return (None)
            else:
                return (a)
        else:
            # if it is an empty line
            return (None)
        
    def parser(self,strict_apl_code):
        """
        Parser Strict APL Code and append the result to source handler.

        Arguments:
            strict_apl_code: code in Strict APL.
        """
        # Parser works in order of lines
        lines = strict_apl_code.splitlines()
        belong_to = []
        belong_to_action = []
        now_belong_to = None
        for each in lines:
            if len(each)==0 :
                continue
            # Very simple driver :)
            now_indent = len(each)-len(each.lstrip())

            now_action = self.expr(each)
            # Prevent the under-overflow.
            if len(belong_to) == 0:
                belong_to.append(now_indent)
                belong_to_action.append(now_action)
                now_belong_to = None
            else:
                if now_indent>belong_to[len(belong_to)-1]:
                    now_belong_to = belong_to_action[len(belong_to)-1]
                    belong_to.append(now_indent)
                    belong_to_action.append(now_action)
                else:
                    if now_indent == belong_to[len(belong_to)-1]:
                        belong_to_action.pop()
                        belong_to_action.append(now_action)
                        # belong_to remains untouched
                    else:
                        # Pop all the indent shorter than the current one
                        while (len(belong_to)>0) and (now_indent<belong_to[len(belong_to)-1]):
                            belong_to_action.pop()
                            belong_to.pop()
                        if len(belong_to)-2>=0:
                            # replace now_belong_to
                            now_belong_to = belong_to_action[len(belong_to)-2]
                        else:
                            now_belong_to = None
                            belong_to=[]
                            belong_to_action = []
                            # Add itself
                            belong_to.append(now_indent)
                            belong_to_action.append(now_action)
                            now_belong_to = None
            # when action built successfully
            if now_action is not None:
                # attach "now_action" to Source
                self.append(now_action.action)
                # attach "now_action" to "now_belong_to" as implementation
                if now_belong_to is not None:
                    now_belong_to.add_implementation(now_action.action)
