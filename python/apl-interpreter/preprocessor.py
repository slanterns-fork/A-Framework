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

import string
import re

class Preprocessor:
    """
    Property:
        code: the code preprocessed with the current Preprocessor
        options: a list which contains some switches
        info: return info of Preprocessor
        fatal_error: true if fatal error has occoured
    """
    
    def __init__(self,raw_code,options={'show_hint':True,'show_warning':True}):
        """
        Arguments:
            raw_code: Your code
            options: A list of options
            {
            'show_hint': Show preprocess hints
            'show_warning': Show preprocess warnings
            }
        """
        self.options = options
        self.code = raw_code
        self.info = []
        self.fatal_error = False
    def extract_builtin(self):
        """
        Extact built-in code and rewrite self.code, the place where the built-in code is will
        be replaced as ?num? , num refers to the builtin_num in builtin_lang and builtin_src.
        
        Return:
            builtin_num: the number of the blocks of built-in code, the number started at zero
            builtin_lang: a list of built-in code languages
            builtin_src: a list of built-in code in other languages
        """
        raw_code = self.code
        self.code = ""
        builtin_mode = False
        received = False
        chars = 0
        builtin_num = -1
        builtin_lang = []
        builtin_src = []
        for i in range(0,len(raw_code)):
            if raw_code[i] == "$" and chars == 0:
                builtin_mode = True
                builtin_num = builtin_num+1
                builtin_lang.append("")
                builtin_src.append("")
            if builtin_mode and raw_code[i] == "{":
                received = True
                chars=chars+1
            if builtin_mode and raw_code[i] == "}":
                received = True
                chars=chars-1
            
            if builtin_mode and (not received):
                builtin_lang[builtin_num]=builtin_lang[builtin_num]+raw_code[i]
            else:
                if builtin_mode and received:
                    builtin_src[builtin_num]=builtin_src[builtin_num]+raw_code[i]

            if not builtin_mode:
                self.code = self.code+raw_code[i]
                
            # clear states
            if received and chars == 0:
                builtin_mode=False
                received = False
                self.code =self.code+"?"+str(builtin_num)+"?"

        if chars <> 0:
            self.info.append("<Error> Unclosed braces found while extracting built-in code blocks.")
            self.fatal_error = True
        return(builtin_num,builtin_lang,builtin_src)
        
    def v1_to_inline (self,options={'indent_space':4}):
        """
        Rewrite APL v1 code using APL v1 inline mode syntax.
        
        Arguments:
            options: A list of options
            {
            'indent_space': Number of sapces added before each lines
            }
            
        Return:
            debug_includes: pass lines strated with "!" to the compiler for integration
        """

        # expand tabs
        self.code = self.code.expandtabs(options['indent_space'])
        
        # clear extra space
        pattern = re.compile("(  ) +")
        self.code = pattern.sub(" ",self.code)
        
        # process the begining char
        self.code = self.code.replace("#",";#")
        self.code = self.code.replace("@",";@")
        self.code = self.code.replace("!",";!")
        self.code = self.code.replace("+",";+")
        
        # split lines
        lines = self.code.splitlines()
        
        # preparing
        self.code = ""
        debug_includes = []

        # process by line
        for each in lines :
            if each.find("+") <>-1 :
                debug_includes.append(each[each.find("+")+1:len(each)].strip())
            else:
                if each.find("#") <> -1:
                    if self.options['show_hint'] :
                        self.info.append("<Hint> Integrate comment into your code. ("+each[each.find("#"):len(each)]+")")
                else:
                    if each.find("@") <> -1:
                        if self.options['show_warning']:
                            self.info.append("<Warning> @ syntax is nerver supported in APL. ("+each[each.find("@"):len(each)]+")")
                    else:
                        if each.find("!") <> -1:
                            if self.options['show_warning']:
                                self.info.append("<Warning> ! syntax is nerver supported in APL. ("+each[each.find("!"):len(each)]+")")
                        else:
                            self.code = self.code + each
        
        # delete extera semicolons
        pattern = re.compile(";+")
        self.code = pattern.sub(";",self.code)
        
        # prepare for APL v1 inline mode
        self.code = self.code.replace(";",'\n')
        self.code = self.code.replace("{","\n{\n")
        self.code = self.code.replace("}","\n}\n")
        
        # return debug_includes which is allowed in APL v1
        return(debug_includes)
    
    def inline_to_strict(self,options={'indent_space':4}):
        """
        Rewrite APL v1 inline code in Strict APL recommended syntax.
        
        Arguments:
            options: A list of options
            {
            'indent_space': Number of sapces added before each lines
            }
        """
        # split lines
        lines = self.code.splitlines()
        
        # preparing
        indent = 0
        self.code = ""
        
        # process by line
        for each in lines:
            if each.strip() == "{":
                indent = indent +1
            else:
                if each.strip() == "}":
                    indent = indent -1
                else:
                    each = each.strip()
                    for i in range(0,indent * options['indent_space']):
                        each = " " + each
                    self.code = self.code + each + "\n"
        if indent <> 0:
            self.info.append("<Error> Unclosed braces found.")
            self.fatal_error = True

    def v2_to_strict(self,options={'indent_space':4}):
        """
        Rewrite APL v2 code in Strict APL recommended syntax.
        
        Arguments:
            options: A list of options
            {
            'indent_space': Number of sapces added before each lines
            }
            
        Return:
            debug_includes: pass lines strated with "!" to the compiler for integration
        """
        # expand tabs
        self.code = self.code.expandtabs(options['indent_space'])
        
        # replace comma with space, which is an Strict APL required syntax
        self.code = self.code.replace(","," ")
        self.code = self.code.replace(";",",")
        
        # split lines
        lines = self.code.splitlines()
        
        # preparing
        debug_includes = []
        self.code = ""
        
        # process by line
        for each in lines :
            if each.find("+") <>-1 :
                debug_includes.append(each[each.find("+")+1:len(each)].strip())
            else:
                if each.find("#") <> -1:
                    if self.options['show_hint'] :
                        self.info.append("<Hint> Integrate comment into your code. ("+each[each.find("#"):len(each)]+")")
                else:
                    if each.find("@") <> -1:
                        if self.options['show_warning']:
                            self.info.append("<Warning> @ syntax is nerver supported in APL. ("+each[each.find("@"):len(each)]+")")
                    else:
                        if each.find("!") <> -1:
                            if self.options['show_warning']:
                                self.info.append("<Warning> ! syntax is nerver supported in APL. ("+each[each.find("!"):len(each)]+")")
                        else:
                            if each.lower().find("define ") == 0:
                                self.code = self.code + each[len("Define "):len(each)] + "\n"
                            else:
                                self.code = self.code + each + "\n"
                                
        # rewrite in Strict APL
        self.code = self.code 
        return(debug_includes)
