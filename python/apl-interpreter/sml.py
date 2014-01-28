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
class SMLHandler(SourceHandler):
    """
    SMLHandler is a SouceHandler which is used to generate or load a
    DOM tree of Scource Markup Language.

    Property:
        info: return info of Interpreter
        fatal_error: true if fatal error has occoured
        options: a list which contains some switches
        source: handling Source object
        dom: DOM
        tree: DOM tree
    """
    import xml.dom.minidom as builder
    def __init__(self, source=None ,options={'show_hint':True,'show_warning':True}):
        """
        Arguments:
            source: source to porcess, none for a new
            options: A list of options
            {
            'show_hint': Show preprocess hints
            'show_warning': Show preprocess warnings
            }
        """
        if source is None:
            self.source = self.Source()
        else:
            self.source = source
        
        self.options = options
        self.info = []
        self.fatal_error = False
        # Reset the DOM tree for the source that will be built later.
        self.dom = self.builder.getDOMImplementation()
        self.tree = self.dom.createDocument("http://cp-web.appspot.com/source", "Source", None)
        
    def build_group_element(self,each_grp):
        groups = self.tree.createElement("Group")
        # add keywords
        for each_grp_kwd in each_grp.keywords:
            keyword = self.tree.createElement("Keyword")
            keyword.appendChild(self.tree.createTextNode(each_grp_kwd))
            groups.appendChild(keyword)
        # add primary key
        if each_grp.primary_key is not None:
            key = self.tree.createElement("Key")
            key.appendChild(self.tree.createTextNode(str(each_grp.primary_key)))
            key.setAttribute("type","primary")
            groups.appendChild(key)
        # add other keys
        for each_grp_k in each_grp.keys:
            key = self.tree.createElement("Key")
            key.appendChild(self.tree.createTextNode(each_grp_k))
            groups.appendChild(key)
        return (groups)
    
    def build_action_element(self,each_act,add_imp=True,must_have_imp=True):
        if not(len(each_act.implementation)==0 and must_have_imp):
            action = self.tree.createElement("Action")      
            # add abstract input object
            for each_obj in each_act.inobjs:
                inputs = self.tree.createElement("Input")
                inputs.setAttribute("id", each_obj)
                for each_grp in each_act.inobjs[each_obj]:
                    inputs.appendChild(self.build_group_element(each_grp))
                action.appendChild(inputs)
                
            # add abstract output object
            for each_obj in each_act.outobjs:
                outputs = self.tree.createElement("Output")
                outputs.setAttribute("id", each_obj)
                for each_grp in each_act.outobjs[each_obj]:
                    outputs.appendChild(self.build_group_element(each_grp))
                action.appendChild(outputs)
                
            if add_imp:
                # add implementation
                implementation = self.tree.createElement("Implementation")
                has_imp=False
                for each_imp in each_act.implementation:
                    RET=self.build_action_element(each_imp,False,False)
                    # add_imp = False to prevent recursion
                    if RET is not None:
                        implementation.appendChild(RET)
                    has_imp=True
                if has_imp:
                    action.appendChild(implementation)

                # add descriptions for the action
                descriptions = self.tree.createElement("Descriptions")
                has_desc=False
                for each_desc in each_act.descriptions:
                    if each_desc[0] is not None:
                        description = self.tree.createElement("Description")
                        description.setAttribute("lang", each_desc[1])
                        description.appendChild(self.tree.createTextNode(each_desc[0]))
                        descriptions.appendChild(description)
                        has_desc=True
                if has_desc:
                    action.appendChild(descriptions)
            return (action)
        else:
            return (None)
    def build_dom_tree(self):
        undescribed_act = 0 # for HINT
        for each_act in self.source.list:
            root = self.tree.documentElement
            RET = self.build_action_element(each_act)
            if RET is not None:
                root.appendChild(RET)
            else:
                undescribed_act = undescribed_act+1 # for HINT
        if self.options['show_hint'] :
            self.info.append("<Hint> This source is not a Complete Knowlege System. (It has "+str(undescribed_act)+" undescribed action in total, and you may have to JOIN another source so that you can run it. )")
    def build_sml(self):
        return(self.tree.toprettyxml(encoding="UTF-8"))

    def read_group_element(self,group_node):
        from group import GroupHandler
        temp_group_handler = GroupHandler()

        nodes = group_node.childNodes
        for current_node in nodes:
            if (current_node.nodeName.lower()=="keyword"):
                temp_group_handler.add_keyword( current_node.childNodes[0].nodeValue)
            if (current_node.nodeName.lower()=="key"):
                temp_group_handler.add_key(current_node.childNodes[0].nodeValue,current_node.getAttribute("type").lower()=="primary")
        return (temp_group_handler.group)
        
    def read_action_element(self,current_action):
        from action import ActionHandler        
        if (current_action.nodeName.lower()=="action"):
            a = ActionHandler()
            nodes = current_action.childNodes
            for current_node in nodes:
                # add abstract input object
                if (current_node.nodeName.lower()=="input"):
                    a.add_in_obj(current_node.getAttribute("id"))
                    for grp in current_node.childNodes:
                        a.add_in_group(current_node.getAttribute("id"),self.read_group_element(grp))
                if (current_node.nodeName.lower()=="output"):
                    a.add_out_obj(current_node.getAttribute("id"))
                    for grp in current_node.childNodes:
                        a.add_out_group(current_node.getAttribute("id"),self.read_group_element(grp))
                if (current_node.nodeName.lower()=="implementation"):
                    for next_level in current_node.childNodes:
                        ret = self.read_action_element(next_level)
                        if ret is not None:
                            a.add_implementation(ret)
                
            return (a.action)
        return None
                
    def read_dom_tree(self):
        for current_action in self.tree.firstChild.childNodes:
            ret = self.read_action_element(current_action)
            if ret is not None:
                self.append(ret)
        
    def read_sml(self,sml_string):
        self.tree = self.builder.parseString(sml_string)
