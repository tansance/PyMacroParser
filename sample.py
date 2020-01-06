# -*- coding: UTF-8 -*-
# @Author   : xgy
class PyMacroParser():
    """docstring for PyMacoParser"""

    def __init__(self):
        self.myMacro = ""   # 读入字符串
        self.addPreMacro = ""   # 增加预定义字符串
        self.dict = {}  # 字典存储

    # 过滤注释
    def filterComment(self, l):
        ### state
        ### 0  正常代码
        ### 1  斜杠
        ### 2  多行注释
        ### 3  多行注释中出现'*'
        ### 4  单行注释
        ### 5  折行注释
        ### 6  字符
        ### 7  字符中的转义字符
        ### 8  字符串
        ### 9  字符串中的转义字符
        state = 0
        flag = 0
        filterAfter = ""
        for eachLine in l:
            for In in range(len(eachLine)):
                cha = eachLine[In]
                if state == 0:
                    if cha == '/':
                        state = 1
                    else:
                        filterAfter += cha
                        if cha == '\'':
                            state = 6
                        elif cha == '\"':
                            state = 8
                    continue
                if state == 1:
                    if cha == '*':
                        state = 3
                    elif cha == '/':
                        state = 4
                    else:
                        filterAfter += '/'
                        filterAfter += cha
                        state = 0
                    continue
                if state == 2:
                    if cha == '*':
                        flag = 1
                        state = 3
                    else:
                        flag = 0
                        #if cha == '\n':
                           #filterAfter += "\r\n"
                        state = 2
                    continue
                if state == 3:
                    if cha == '/':
                        #filterAfter += '\r\n'
                        if flag == 1:
                            filterAfter += ' '
                        state = 0
                    elif cha == '*':
                        flag = 1
                        state = 3
                    else:
                        flag = 0
                        state = 2
                    continue
                if state == 4:
                    if cha == '\\':
                        state = 5
                    elif cha == '\n':
                        filterAfter += "\r\n"
                        state = 0
                    else:
                        state = 4
                    continue
                if state == 5:
                    if cha == '\\' or cha == '\r' or cha== '\n':
                        if cha == '\n':
                           filterAfter += "\r\n"
                        state = 5
                    else:
                        state = 4
                    continue
                if state == 6:
                    filterAfter += cha
                    if cha == '\\':
                        state = 7
                    elif cha == '\'':
                        state = 0
                    else:
                        state = 6
                    continue
                if state == 7:
                    filterAfter += cha
                    state = 6
                    continue
                if state == 8:
                    filterAfter += cha
                    if cha == '\\':
                        state = 9
                    elif cha == '\"':
                        state = 0
                    else:
                        state = 8
                    continue
                if state == 9:
                    filterAfter += cha
                    state = 8
                    continue
        return  filterAfter

    # 处理ifdef等分支
    def deelWithIfelse(self, macro):
        #waitList = self.deelString(macro)
        waitList = self.deelStringtest(macro)
        # print waitList
        stack = []  # 创建if-else匹配栈
        self.dict = {}
        for tra in waitList:
            keywords = tra[0]
            name = tra[1]
            value = tra[2]
            if keywords == 'ifdef':
                if stack == [] or stack[-1] == 'light':
                    if self.dict.get(name) != None:
                        stack.append('light')
                    else:
                        stack.append('dark')
                elif stack[-1] == 'dark' or stack[-1] == 'inComment':
                    stack.append('inComment')
            elif keywords == 'ifndef':
                if stack == [] or stack[-1] == 'light':
                    if self.dict.get(name) == None:
                        stack.append('light')
                    else:
                        stack.append('dark')
                elif stack[-1] == 'dark' or stack[-1] == 'inComment':
                    stack.append('inComment')
            elif keywords == 'define':
                if stack == [] or stack[-1] == 'light':
                    self.dict[name] = value
            elif keywords == 'endif':
                if stack != []:
                    del stack[-1]
            elif keywords == 'else':
                if stack == []:
                    raise Exception('empty stack')
                if stack[-1] == 'light':
                    stack[-1] = 'dark'
                elif stack[-1] == 'dark':
                    stack[-1] = 'light'
            elif keywords == 'undef':
                if stack == [] or stack[-1] == 'light':
                    del self.dict[name]

    #读取文件内容
    def load(self,f): #读取cpp中宏定义
        try:
            read_file = open(f, 'r')
        except IOError:
            print 'no file'
        else:
            result = list()
            for line in read_file:
                line = line.lstrip()
                if len(line):
                    result.append(line)
            read_file.close()
            #print result
            self.myMacro = self.filterComment(result) + '\r\n'
            #self.myMacro = self.myMacro.replace('#', '/r#')

            self.addPreMacro = self.myMacro
            #print self.myMacro
            self.deelWithIfelse(self.myMacro)

    # 在最前面添加预定义宏
    def preDefine(self, s):
        tmp = s.split(';')
        #print tmp
        preMacro = ""
        for each in tmp:
            if each != '':
                preMacro += "#define " + each + '\r\n'
        self.addPreMacro = preMacro + self.myMacro
        self.deelWithIfelse(self.addPreMacro)


    # 处理字符串，去除空行做列表管理list[0] = keywords ; list[1] = name ; list[2] = value
    def deelStringtest(self,macro):
        tmpOut = open('tmpfile.cpp','w')
        tmpOut.write(macro)
        tmpOut.close()
        tmpIn = open('tmpfile.cpp','r')
        lines = tmpIn.readlines()
        tmpIn.close()
        list = []
        for s in lines:
            s = self.deeltab(s)
            s = s.strip()
            if s != '' and s[0] == '#':
                s = s[1:]
                s = s.strip()
                t = s.split(' ', 1)
                keywords = t[0]
                if keywords == 'else' or keywords == 'endif':
                    list.append([keywords, 'None', 'None'])
                elif keywords == 'ifdef' or keywords == 'ifndef' or keywords == 'undef':
                    ss = t[1].strip()
                    tt = ss.split(' ', 1)
                    list.append([keywords, tt[0], 'None'])
                elif keywords == 'define':
                    ss = t[1].strip()
                    tt = ss.split(' ', 1)
                    if len(tt) == 2:
                        list.append([keywords, tt[0], tt[1].strip()])
                    elif len(tt) == 1:
                        list.append([keywords, tt[0], 'None'])
        return list

    # 处理字符串中可能出现的tab
    def deeltab(self,s):
        stmp = ''
        stack = []
        for k in s:
            if stack == []:
                if k == '\'' or k == '\"':
                    stack.append(k)
            else:
                if k == '\'' or k == '\"':
                    if stack[0] == k:
                        stack = []
                    else:
                        stack.append(k)
            if k == '\t' and stack == []:
                stmp += ' '
            stmp += k
        return stmp

    # 将字符串进行对其他数据类型的转换
    def string2other(self,s):
        s = s.strip()
        if s == '':
            return s
        elif s == 'false':  # bool
            return False
        elif s == 'true':
            return True
        elif s == 'None':
            return None
        elif s[0] == '\'' and s[-1] == '\'':  # 字符常量
            s = s[1:-1]
            hexlist = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C',
                       'D', 'E', 'F']
            octallist = ['0', '1', '2', '3', '4', '5', '6', '7']
            escape_dict = {'\\': '\\', '\'': '\'', '\"': '\"', 'a': '\a', 'b': '\b', 'n': '\n', 'v': '\v', 't': '\t',
                           'r': '\r','f':'\f'}
            if len(s) > 3:
                if s[-4] == '\\':
                    if s[-3] == 'x':
                        if s[-1] in hexlist and s[-2] in hexlist:
                            return int('0'+ s[-3:], 16)
                    elif s[-3] in octallist and s[-2] in octallist and s[-1] in octallist:
                        return int(s[-3:],8)
            if len(s) >2:
                if s[-3] == '\\':
                    if s[-2] in octallist and s[-1] in octallist:
                        return int(s[-2:],8)
            if len(s) >1:
                if s[-2] == '\\':
                    if s[-1] in octallist:
                        return int(s[-1],8)
                    if s[-1] in escape_dict:
                        return ord(escape_dict[s[-1]])
            if len(s) >0:
                return ord(s[-1])


        elif s[0] == '\"' and s[-1] == '\"':  # 字符串
            s = s[1:-1]
            flag = 1
            stringTmp = ''
            for i in range(len(s)):
                if i < len(s) - 1:
                    if s[i] == '\\' and s[i+1] == '\"':
                        stringTmp += '\\'
                        continue
                if flag == 1 and s[i] != '\"':
                    stringTmp += s[i]
                if s[i] == '\"':
                    if i > 0:
                        if s[i - 1] == '\\':
                            stringTmp += s[i]
                        else:
                            flag *= -1
                    elif i == 0:
                        flag *= -1
            tt = ''
            #escape = ['\\','\'','\"','a','b','n','v','t','r']
            escape_dict = {'\\':'\\','\'': '\'','\"':'\"','a':'\a','b':'\b','n':'\n','v':'\v','t':'\t','r':'\r','f':'\f'}
            hexlist = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','A','B','C','D','E','F']
            octallist = ['0','1','2','3','4','5','6','7']
            k = 0
            while(k < len(stringTmp)):
                if stringTmp[k] == '\\':
                    if k < len(stringTmp) - 1:
                        if  k < len(stringTmp) -2:
                            if k < len(stringTmp) - 3:
                                if stringTmp[k+1] in octallist and stringTmp[k+2] in octallist and stringTmp[k+3] in octallist:
                                    ss = stringTmp[k+1]+stringTmp[k+2]+stringTmp[k+3]
                                    tt += chr(int(ss,8))
                                    k += 4
                                    continue
                                elif stringTmp[k + 1] == 'x':
                                    if stringTmp[k+2] in hexlist and stringTmp[k+3] in hexlist:
                                        ss = '0' + stringTmp[k+1]+stringTmp[k+2]+stringTmp[k+3]
                                        tt += chr(int(ss,16))
                                        k += 4
                                        continue
                            elif stringTmp[k + 1] in octallist and stringTmp[k + 2] in octallist:
                                ss = stringTmp[k + 1] + stringTmp[k + 2]
                                tt += chr(int(ss, 8))
                                k += 3
                                continue
                            elif stringTmp[k+1] == 'x' and stringTmp[k + 2] in hexlist:
                                ss = '0' + stringTmp[k+1] + stringTmp[k+2]
                                tt += chr(int(ss,16))
                                k += 4
                                continue
                        if stringTmp[k + 1] in octallist:
                            ss = stringTmp[k + 1]
                            tt += chr(int(ss, 8))
                            k += 2
                            continue
                        if stringTmp[k+1] in escape_dict:
                            tt += escape_dict[stringTmp[k+1]]
                        else:
                            tt += stringTmp[k + 1]
                        k += 2
                        continue
                else:
                    tt += stringTmp[k]
                    k += 1
            return tt
        elif s[0] == 'L' :
            s = s[2:-1]
            flag = 1
            stringTmp = ''
            for i in range(len(s)):
                if i < len(s) - 1:
                    if s[i] == '\\' and s[i+1] == '\"':
                        stringTmp += '\\'
                        continue
                if flag == 1 and s[i] != '\"':
                    stringTmp += s[i]
                if s[i] == '\"':
                    if i > 0:
                        if s[i - 1] == '\\':
                            stringTmp += s[i]
                        else:
                            flag *= -1
                    elif i == 0:
                        flag *= -1
            tt = ''
            #escape = ['\\','\'','\"','a','b','n','v','t','r']
            escape_dict = {'\\':'\\','\'': '\'','\"':'\"','a':'\a','b':'\b','n':'\n','v':'\v','t':'\t','r':'\r','f':'\f'}
            k = 0
            while(k < len(stringTmp)):
                if stringTmp[k] == '\\':
                    if k < len(stringTmp) - 1:
                        if k < len(stringTmp) - 3:
                            if stringTmp[k+1:k+4].isdigit() == True:
                                ss = stringTmp[k+1]+stringTmp[k+2]+stringTmp[k+3]
                                tt += chr(int(ss,8))
                                k += 4
                                continue
                            elif stringTmp[k + 1] == 'x':
                                ss = '0' + stringTmp[k+1]+stringTmp[k+2]+stringTmp[k+3]
                                tt += chr(int(ss,16))
                                k += 4
                                continue
                        if stringTmp[k+1] in escape_dict:
                            tt += escape_dict[stringTmp[k+1]]
                        else:
                            tt += stringTmp[k + 1]
                        k += 2
                        continue
                else:
                    tt += stringTmp[k]
                    k += 1
            return unicode(tt)
        elif s[0] == '{' :
            if s[-1] == ';':
                s = s[1:-2]
            else:
                s = s[1:-1]
            mysplit = []
            mark = 1
            stack = []
            stack2 = []
            sTmp = ''
            for index in range(len(s)):
                if s[index] == ','  and stack == [] and stack2 == []:
                    mysplit.append(sTmp.strip())
                    sTmp = ''
                    continue
                if s[index] == '\'' or s[index] == '\"':
                    if stack2 == []:
                        stack2.append(s[index])
                    else:
                        if s[index] == stack2[0]:
                            stack2 = []
                        else:
                            stack2.append(s[index])
                if s[index] == '{' and stack2 == []:
                    stack.append('{')
                if s[index] == '}' and stack2 == []:
                    del stack[-1]
                sTmp += s[index]
                if index == len(s) - 1:
                    mysplit.append(sTmp.strip())
            list2tuple = []
            for k in mysplit:
                list2tuple.append(self.string2other(k))
            return tuple(list2tuple)

        elif s[0] == '-' or s[0] == '+':
            sign_flag = 1
            for i in range(len(s)):
                if s[i] == '-' or s[i] == '+' or s[i] == ' ':
                    if s[i] == '-':
                        sign_flag *= -1
                else:
                    s = s[i:]
                    break
            float_flag = 0
            for t in s:
                if t == '.' or t == 'e' or t == 'E' or s[-1] == 'f' or s[-1] == 'F':
                    float_flag = 1
                if s[:2] == '0x' or s[:2] == '0X':
                    float_flag = 0
            if float_flag == 0:
                if len(s) > 4 and (s[-3:] == 'i64' or s[-3:] == 'I64'):
                    s = s[:-3]
                elif len(s) > 3 and (s[-2:] == 'll' or s[-2:] == 'LL'):
                    s = s[:-2]
                elif len(s) > 2 and (s[-1] == 'l' or s[-1] == 'L'):
                    s = s[:-1]
                if s[0] == '0':
                    if s == '0':
                        return int(s)*sign_flag
                    elif s[1] == 'x' or s[1] == 'X':
                        return int(s, 16)*sign_flag
                    elif s[1] == 'b' or s[1] == 'B':
                        return int(s, 2)*sign_flag
                    else:
                        return int(s, 8)*sign_flag
                else:
                    return int(s)*sign_flag
            else:
                if (s[-1] == 'f' or s[-1] == 'l'
                        or s[-1] == 'F' or s[-1] == 'L'):
                    s = s[:-1]
                return float(s)*sign_flag
        else:
            float_flag = 0
            for t in s:
                if t == '.' or t == 'e' or t == 'E' or s[-1] == 'f' or s[-1] == 'F':
                    float_flag = 1
                if s[:2] == '0x' or s[:2] == '0X':
                    float_flag = 0
            if float_flag == 0:
                if len(s) > 4 and (s[-4:] == 'ui64' or s[-4:] == 'uI64'
                                        or s[-4:] == 'Ui64' or s[-4] == 'UI64'):
                    s = s[:-4]
                elif len(s) > 3 and (s[-3:] == 'i64' or s[-3:] == 'I64'
                                          or s[-3:] == 'ull' or s[-3:] == 'uLL'
                                          or s[-3:] == 'Ull' or s[-3:] == 'ULL'):
                    s = s[:-3]
                elif len(s) > 2 and (s[-2:] == 'll' or s[-2:] == 'LL'
                                          or s[-2:] == 'ul' or s[-2:] == 'Ul'
                                          or s[-2:] == 'uL' or s[-2:] == 'UL'):
                    s = s[:-2]
                elif (s[-1] == 'u' or s[-1] == 'U'
                      or s[-1] == 'l' or s[-1] == 'L'):
                    s = s[:-1]
                if s[0] == '0':
                    if s == '0':
                        return int(s)
                    elif s[1] == 'x' or s[1] == 'X':
                        return int(s, 16)
                    elif s[1] == 'b' or s[1] == 'B':
                        return int(s, 2)
                    else:
                        return int(s, 8)
                else:
                    return int(s)
            else:
                if (s[-2:] == 'lf' or s[-2:] == 'LF' or s[-2:] == 'lF' or s[-2:] == 'Lf'):
                    s = s[:-2]
                if (s[-1] == 'f' or s[-1] == 'l'
                        or s[-1] == 'F' or s[-1] == 'L'):
                    s = s[:-1]
                tt = s.split(' ')
                s = ''
                for k in tt:
                    s += k
                return float(s)

    # 对数据处理，转换成python内部数据类型
    def dictDataConversion(self, d):
        #print d
        for key in d:
            d[key] = self.string2other(d[key])
        return d

    # 对字典数据再处理，转换成cpp数据类型
    def dataInCpp(self,d):
        cppDict = {}
        d = self.dictDataConversion(d)
        for key in d:
            valueType = type(d[key])
            if d[key] == None:
                cppDict[key] = 'None'
            elif valueType == int or valueType == long:
                cppDict[key] = d[key]
            elif valueType == float:
                cppDict[key] = d[key]
            elif valueType == unicode:
                escape_dict = {'\\':'\\\\','\'':'\\\'','\"':'\\\"','\a':'\\a','\b':'\\b','\n':'\\n','\v':'\\v','\t':'\\t','\r':'\\r','\f':'\\f'}
                ss = ''
                for k in d[key]:
                    if k in escape_dict:
                        ss += escape_dict[k]
                    else:
                        ss += k
                cppDict[key] = 'L'+'\"'+ ss + '\"'
            elif valueType == str:
                escape_dict = {'\\':'\\\\','\'':'\\\'','\"':'\\\"','\a':'\\a','\b':'\\b','\n':'\\n','\v':'\\v','\t':'\\t','\r':'\\r','\f':'\\f'}
                ss = ''
                for k in d[key]:
                    if k in escape_dict:
                        ss += escape_dict[k]
                    else:
                        ss += k
                cppDict[key] = '\"' + ss + '\"'
            elif valueType == tuple:
                l = []
                self.tuple2cpp(d[key],l)
                cppDict[key] = l
            elif valueType == bool:
                if d[key] == True:
                    cppDict[key] = 'true'
                else:
                    cppDict[key] = 'false'
        return cppDict

    # 对特殊类型tuple的解析
    def tuple2cpp(self,t,l):
        l.append('{')
        for k in t:
            if type(k) == tuple:
                l.append(self.tuple2cpp(k,l))
            elif type(k) == str:
                l.append('\"')
                escape_dict = {'\\': '\\\\', '\'': '\\\'', '\"': '\\\"', '\a': '\\a', '\b': '\\b', '\n': '\\n',
                               '\v': '\\v', '\t': '\\t', '\r': '\\r','\f':'\\f'}
                ss = ''
                for tt in k:
                    if tt in escape_dict:
                        ss += escape_dict[tt]
                    else:
                        ss += tt
                l.append(ss)
                l.append('\"')
            elif type(k) == unicode:
                l.append('L\"')
                escape_dict = {'\\': '\\\\', '\'': '\\\'', '\"': '\\\"', '\a': '\\a', '\b': '\\b', '\n': '\\n',
                               '\v': '\\v', '\t': '\\t', '\r': '\\r','\f':'\\f'}
                ss = ''
                for tt in k:
                    if tt in escape_dict:
                        ss += escape_dict[tt]
                    else:
                        ss += tt
                l.append(ss)
                l.append('\"')
            elif type(k) == bool:
                if k == True:
                    l.append('true')
                else:
                    l.append('false')
            else:
                l.append(k)
            if k != t[-1]:
                l.append(', ')
        l.append('}')

    # 产生返回字典
    def dumpDict(self):
        dictconv = {}
        for key in self.dict:
            dictconv[key] = self.dict[key]
        dictconv = self.dictDataConversion(dictconv)
        print dictconv
        return dictconv

    # 返回输出cpp
    def dump(self, f):
        dCpp = {}
        for key in self.dict:
            dCpp[key] = self.dict[key]
        #print dict
        dCpp = self.dataInCpp(dCpp)
        try:
            myfile = open(f, 'w')
        except IOError:
            print 'no file'
        else:
            for key in dCpp:
                if dCpp[key] == 'None':
                    myfile.write('#define ' + key + '\n')
                elif type(dCpp[key]) == list:
                    myfile.write('#define ' + key + ' ')
                    for k in dCpp[key]:
                        if k != None:
                            myfile.write(str(k))
                    myfile.write('\n')
                else:
                    myfile.write('#define ' + key +' ' + str(dCpp[key]) + '\n')
            myfile.close()

if __name__ == '__main__':
    a1 = PyMacroParser()
    a2 = PyMacroParser()
    a1.load("b.cpp")
    a1.dumpDict()