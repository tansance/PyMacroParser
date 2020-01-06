#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import string

ESCAPE = {'\\':'\\','\'': '\'','\"':'\"','a':'\a','b':'\b','n':'\n','v':'\v','t':'\t','r':'\r','f':'\f'}
ESCAPE_CHAR = ['\\','\'','\"','a','b','n','v','t','r','f']
HEX = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']
OCTAL = ['0','1','2','3','4','5','6','7']

class PyMacroParser:
    def __init__(self):
        self._raw_dict = {} # valid macro with value untranslated
        self._trans_dict = {} # valid macro with value translated
        self._raw_macro = [] # original file content
        self._filtered_macro = [] # macro added pre define macro, filtered comment

    def load(self, file_path):
        """
        load file, pre-processing file content
        :param file_path: string, path of file will be loaded
        :return: void
        """
        try:
            file = open(file_path, 'r')
        except IOError:
            print "Error: file path error.\n"
            raise IOError
        self._raw_macro = self.pre_processing(file)
        file.close()
        # for line in self._raw_macro:
        #     print line
        self._filtered_macro = self._raw_macro
        self.filter_ifelse(self._filtered_macro)

    def preDefine(self, s):
        """
        add macro in s to the beginning of self._raw_macro
        :param s: string, macro added to raw macro
        :return: void
        """
        if s == '':
            return
        pre_macro = []
        s = s.split(';')
        for macro in s:
            if macro != '':
                pre_macro.append('#define ' + macro)
        self._filtered_macro = pre_macro + self._raw_macro
        # reorganize self._filtered_macro to self._raw_dict
        self.filter_ifelse(self._filtered_macro)

    def dumpDict(self):
        """
        translate raw dictionary's value to py type
        store in self._trans_dict and return
        :return: dictionary
        """
        self._trans_dict.clear()
        for k in self._raw_dict.keys():
            if self._raw_dict[k] != None:
                self._trans_dict[k] = self.cpp_to_py(self._raw_dict[k])
            else:
                self._trans_dict[k] = None
        print self._trans_dict
        return self._trans_dict

    def dump(self, file_path):
        """
        output filtered macro to file whose path is file_path
        :param file_path: string, path of file outputted
        :return: void
        """
        try:
            output_file = open(file_path, 'w')
        except IOError:
            print "Error: file path error.\n"
            raise IOError
        self.dumpDict()
        for key in self._trans_dict.keys():
            # deal with None value macro
            if self._trans_dict[key] is None:
                output_file.write('#define ' + key + '\n')
            else:
                value = self.py_to_cpp(self._raw_dict[key], self._trans_dict[key])
                output_file.write('#define ' + key + ' ' + value + '\n')
        output_file.close()

    def tuple_to_structure(self, struct, tup):
        """
        convert tuple to cpp structure
        :param struct: string, original cpp structure
        :param tup: tuple, python tuple
        :return: string, structure converted from python tuple
        """
        origin = self.split_cpp_struct(struct)
        value = '{'
        i = 0
        while i < len(origin):
            temp = self.py_to_cpp(origin[i], tup[i])
            value += temp + ', '
            i += 1
        value = value[:-2] + '}'
        return value

    def py_to_cpp(self, cpp, py):
        """
        convert python types back to cpp type
        :param cpp: string, original cpp type
        :param py: python types,
        :return: string, cpp types converted from python types
        """
        value = ''
        # int, long, float, char
        t = type(py)
        if t is int or t is float or t is long:
            value = str(py)
        # structure
        elif t is tuple:
            value = self.tuple_to_structure(cpp, py)
        # bool
        elif t is bool:
            value = str(py).lower()
        # string or long string
        elif t is unicode or t is str:
            value = cpp
        return value


    def filter_ifelse(self, macro):
        """
        filter if else clause according to macro, translate cpp macro to python type
        translate cpp macro to python dictionary and stored in self._trans_dict
        :param macro: [string(line)], macro content with newly added macro
        :return:
        """
        self._raw_dict.clear()
        stack = [True]
        # split macro sentences into words
        macro_split = []
        for m in macro:
            temp = []
            m = self.replace_tabs(m)
            m = m.strip()
            m = m[1:].strip()
            # get define clause
            list = m.split(' ', 1)
            temp.append(list[0])
            # get variable
            if temp[0] != 'endif' and temp[0] != 'else':
                list = list[1].strip().split(' ', 1)
                temp.append(list[0].strip())
                # get value if exists
                if len(list) == 2:
                    temp.append(list[1].strip())
            macro_split.append(temp)
        # filter valid macro out from if-else clause
        for m in macro_split:
            # when clauses are in invalid area
            if stack[-1] is not True:
                if m[0] == 'ifdef' or m[0] == 'ifndef':
                    stack.append('invalid')
                elif m[0] == 'endif':
                    stack.pop()
                elif m[0] == 'else' and stack[-1] != 'invalid':
                    stack[-1] = not stack[-1]
                continue
            # when clauses are in valid area
            if m[0] == 'ifdef' and m[1] not in self._raw_dict.keys():
                stack.append(False)
            elif m[0] == 'ifdef' and m[1] in self._raw_dict.keys():
                stack.append(True)
            elif m[0] == 'ifndef' and m[1] not in self._raw_dict.keys():
                stack.append(True)
            elif m[0] == 'ifndef' and m[1] in self._raw_dict.keys():
                stack.append(False)
            elif m[0] == 'else':
                stack[-1] = not stack[-1]
            elif m[0] == 'endif':
                if len(stack) != 1:
                    stack.pop()
            # store untranslated value in dictionary
            elif m[0] == 'define':
                if len(m) >= 3:
                    temp = ''
                    for word in m[2:]:
                        temp += word + ' '
                    temp = temp[:-1]
                    self._raw_dict[m[1]] = temp
                else:
                    self._raw_dict[m[1]] = None
            # deal with undef clause
            elif m[0] == 'undef':
                del self._raw_dict[m[1]]

    def replace_tabs(self, s):
        """
        replace tabs with signle space
        :param s: string, cpp code
        :return: string, replaced cpp code
        """
        stack = []
        intabs = -1
        i = 0
        res = ''
        while i < len(s):
            if len(stack) == 0:
                if s[i] != '\t':
                    if intabs == -1:
                        res += s[i]
                    else:
                        res += ' ' + s[i]
                        intabs = -1
                    if s[i] == '\'' or s[i] == '\"':
                        stack.append(s[i])
                else:
                    intabs = i
            else:
                res += s[i]
                if (s[i] == '\'' or s[i] == '\"') and s[i] == stack[-1]:
                    stack.pop()
            i += 1
        return res.strip()

    def cpp_to_py(self, s):
        """
        convert cpp type to python type
        :param s: string, cpp type
        :return: python type
        """
        value = None
        if s == '':
            return s
        elif s == 'None':
            return None
        # boolean
        elif s == 'true':
            value = True
        elif s == 'false':
            value = False
        # string, need convert escape character
        elif s[0] == '\"' and s[-1] == '\"':
            value = ''
            s = s[1:-1]
            i = 0
            status = 0
            while(i < len(s)):
                # escape characters
                if s[i] == '\\' and i < len(s) - 1 and s[i+1] in ESCAPE.keys():
                    value += ESCAPE[s[i+1]]
                    i += 1
                # data needs concat
                elif status == 0 and s[i] == '\"':
                    status = 1
                # exit concat mode
                elif status == 1 and s[i] == '\"':
                    status = 0
                elif status == 0:
                    value += s[i]
                i += 1

        # long string
        elif s[0] == 'L':
            value = ''
            s = s[2:-1]
            i = 0
            while (i < len(s)):
                # escape characters
                if s[i] == '\\' and i < len(s) - 1 and s[i + 1] in ESCAPE.keys():
                    value += ESCAPE[s[i + 1]]
                    i += 1
                else:
                    value += s[i]
                i += 1
            value = unicode(value)
        # char
        elif s[0] == '\'' and s[-1] == '\'':
            s = s[1:-1]
            if len(s) > 3:
                if s[-4] == '\\':
                    if s[-3] == 'x':
                        if s[-1] in HEX and s[-2] in HEX:
                            value = int('0' + s[-3:], 16)
                    elif s[-3] in OCTAL and s[-2] in OCTAL and s[-1] in OCTAL:
                        value = int(s[-3:], 8)
            elif len(s) == 3:
                if s[0] == '\\':
                    if s[1] in OCTAL and s[2] in OCTAL:
                        value = int(s[1:], 8)
            elif len(s) == 2:
                if s[0] == '\\':
                    if s[1] in OCTAL:
                        value = int(s[1], 8)
                    elif s[1] in ESCAPE.keys():
                        value = ord(ESCAPE[s[1]])
            else:
                value = ord(s)
        # structure
        elif s[0] == '{' and s[-1] == '}':
            value = self.make_tuple(s)
        # int, float, hex, octal
        else:
            s, status, sign = self.check_number_status(s)
            value = self.cpp_number_py(s, status, sign)
        return value

    def check_number_status(self, s):
        """
        check the type of s,
        status = 0 => s is int
        status = 1 => s is hex
        status = 2 => s is oct
        status = 3 => s is float
        :param s: string, value
        :return: string, int, int: tailored s, status, sign of number
        """
        sign = 1
        status = 0
        # deal with sign
        if s[0] == '+':
            s = s[1:]
        elif s[0] == '-':
            sign = -1
            s = s[1:]
        # hex
        if len(s) > 2 and s[0] == '0' and (s[1] == 'x' or s[1] == 'X'):
            status = 1
        # octal
        elif len(s) > 1 and s[0] == '0' and (s[1] in OCTAL):
            status = 2
        # float
        else:
            while s[-1].isalpha():
                s = s[:-1]
            for d in s:
                if not d.isdigit():
                    status = 3
                    break
        return s, status, sign

    def cpp_number_py(self, s, status, sign):
        """
        translate cpp number to python number
        :param s: string, value
        :param status: int, type of number
        :param sign: int, sign of number
        :return: int or float
        """
        # hex
        if status == 1:
            if s[-1] not in HEX:
                s = s[:-1]
            value = int(s, 16) * sign
        # octal
        elif status == 2:
            value = int(s, 8) * sign
        # float
        elif status == 3:
            value = float(s) * sign
        # int
        elif status == 0:
            value = int(s) * sign
        return value

    def make_tuple(self, s):
        """
        cpp structure to py tuple
        :param s: string, contains cpp structure
        :return: tuple
        """
        value = []
        elems = self.split_cpp_struct(s)
        for e in elems:
            if e[0] == '{':
                sub_value = self.make_tuple(e)
                value.append(sub_value)
            else:
                value.append(self.cpp_to_py(e))
        return tuple(value)

    def split_cpp_struct(self, s):
        """
        split structure by the most outside comma
        :param s: string, cpp structure
        :return: [string], each string is one element of cpp structure
        """
        stack = []
        prev = ''
        s = s[1:-1]
        s = s.strip()
        if s[-1] == ',':
            s = s[:-1]
        elements = []
        split_point = [0]
        i = 0
        # get index of split point
        while i < len(s):
            if stack == []:
                if s[i] == ',':
                    split_point.append(i)
                elif s[i] == '{' or s[i] == '\'' or s[i] == '\"':
                    stack.append(s[i])
            else:
                # in string
                if stack[-1] == '\'' or stack[-1] == '\"':
                    if prev != '\\' and s[i] == stack[-1]:
                        stack.pop()
                # in sub structure
                elif stack[-1] == '{':
                    if s[i] == '{' or s[i] == '\'' or stack[-1] == '\"':
                        stack.append(s[i])
                    elif s[i] == '}':
                        stack.pop()
            prev = s[i]
            i += 1

        if len(split_point) == 1:
            elements.append(s.strip())
        else:
            i = 1
            elements.append(s[split_point[0]:split_point[1]].strip())
            while i < len(split_point) - 1:
                elements.append(s[split_point[i] + 1:split_point[i+1]].strip())
                i += 1
            elements.append(s[split_point[-1]+1:].strip())
        return elements


    def pre_processing(self, file):
        """
        :param file:
        :return:
        """
        return self.filter_comment(file)

    def filter_comment(self, file):
        status = 0
        file_content = []
        for line in file:
            after_filter = ''
            for c in line:
                if status == 0:
                    if c == '/':
                        status = 1
                    elif c == '\'':
                        status = 4
                    elif c == '\"':
                        status = 5
                    after_filter += c
                    continue
                if status == 1:
                    # in single line comment
                    if c == '/':
                        after_filter = after_filter[:-1]
                        status = 0
                        break
                    # in multi line comment
                    elif c == '*':
                        after_filter = after_filter[:-1]
                        status = 2
                    else:
                        after_filter += c
                        status = 0
                    continue
                # in multi line comment
                if status == 2:
                    if c == '*':
                        status = 3
                    continue
                # ready end multi line comment
                if status == 3:
                    # end multi line comment
                    if c == '/':
                        after_filter += ' '
                        status = 0
                    elif c == '*':
                        continue
                    # restart multi line comment
                    else:
                        status = 2
                    continue
                # in string
                if status == 4:
                    if c == '\\':
                        status = 6
                    if c == '\'':
                        status = 0
                    after_filter += c
                    continue
                if status == 5:
                    if c == '\\':
                        status = 7
                    if c == '\"':
                        status = 0
                    after_filter += c
                    continue
                # ready escape
                if status == 6:
                    after_filter += c
                    status = 4
                if status == 7:
                    after_filter += c
                    status = 5
            after_filter = after_filter.strip()
            if after_filter != '':
                if after_filter[0] != '#':
                    last = file_content[-1]
                    file_content[-1] = file_content[-1] + ' ' + after_filter
                else:
                    file_content.append(after_filter)
        return file_content