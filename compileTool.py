import shutil
import sys
import os
import win32api
import win32con
import glob
import time



def findAllSrcFile(ab_dir,sSrcFile):  # src目录下的所有文件及其子目录内的文件
    sSrc = glob.glob(ab_dir)
    if not sSrc:
        return 0
    for file in sSrc:
        if os.path.isfile(file) and (('.c' in file) or ('.cpp' in file)) and 'pyc' not in file:
            sSrcFile.append(file)
        elif os.path.isdir(file):  # 这时候需要继续迭代
            path = file + '/*'
            findAllSrcFile(path,sSrcFile)


def findALLLibFile(ab_dir,sLIB,slibFolder):
    sLib = glob.glob(ab_dir)
    if not sLib:
        return 0
    for file in sLib:
        if os.path.isfile(file) and (('.lib' in file) or ('.a' in file)):
            sLIB.append(file)
            slibFolder.append(os.path.split(file)[0])
        elif os.path.isdir(file):  # 这时候需要继续迭代
            slibFolder.append(file)
            path = file + '/*'
            findALLLibFile(path,sLIB,slibFolder)


def findALLDllFile(ab_dir,sDLL):
    sDll = glob.glob(ab_dir)
    if not sDll:
        return 0
    for file in sDll:
        if os.path.isfile(file) and '.dll' in file and ('.a' not in file):
            sDLL.append(file)
        elif os.path.isdir(file):  # 这时候需要继续迭代
            path = file + '/*'
            findALLDllFile(path,sDLL)


def findALLIncludeFile(ab_dir,sInclude,sIncludefolder):
    sinclude_ = glob.glob(ab_dir)
    if not sinclude_:
        return 0
    for file in sinclude_:
        if os.path.isfile(file) and (('.h' in file) or ('.c' in file) or ('.hpp' in file)):
            if "tbb" not in os.path.split(file)[0]:
                sIncludefolder.append(os.path.split(file)[0])
            if "armadillo" in os.path.split(file)[0]:
                pass
            else:
                sInclude.append(file)
            # sIncludefolder.append(os.path.split(file)[0])
        elif os.path.isdir(file):  # 这时候需要继续迭代
            if "tbb" not in file:
                sIncludefolder.append(file)
            path = file + '/*'
            findALLIncludeFile(path,sInclude,sIncludefolder)


def WriteMake(ab_dir, projectName, sSrcFile, sDLL, sLIB, sInclude, slibFolder, sIncludefolder):
    str_ = 'add_executable({}\n'.format(projectName)
    for srcFile in set(sSrcFile):
        srcFile = srcFile.replace('\\', '/')
        str_ += srcFile + '\n'
    for header in set(sInclude):
        header = header.replace('\\', '/')
        str_ += header + '\n'
    str_ += 'D:/ProgramData/Anaconda3/include/Python.h' + '\n'
    str_ += ')\n'
    str_.replace('i', 'iiiiiiiiiiii')
    with open(ab_dir + '/CMakeLists.txt', 'w')as f:
        f.write('cmake_minimum_required(VERSION 3.14)\n')
        f.write('project({})\n'.format(projectName))
        f.write('set(CMAKE_CXX_STANDARD 17)\n')
        # f.write('set(CMAKE_CXX_COMPILER "C:/msys64/mingw64/bin/clang++")\n')
        # f.write('set(CMAKE_C_COMPILER   "C:/msys64/mingw64/bin/clang")\n')
        f.write('set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")\n')
        f.write('set(CMAKE_EXE_LINKER_FLAGS "-static-libgcc -static-libstdc++")\n')
        f.write('set(CMAKE_CXX_FLAGS_RELEASE "-O3")\n')
        f.write('set(CMAKE_CXX_FLAGS_DEBUG "-O2")   \n')
        f.write('include_directories(include)\n')
        # f.write('include_directories(E:/CPPTOOL/eigen337)\n')
        # f.write('include_directories(E:/CPPTOOL/nolhmann)\n')
        f.write('include_directories(E:/CLionProjects/MYtoolTest/MyTool/include)\n')

        f.write(
            'include_directories(D:/ProgramData/Anaconda3/include)\n')  # 还要把python的inlcude文件夹添加进来，因为有可能和python交互，用到python.h
        for dir in set(sIncludefolder):
            dir = dir.replace('\\', '/')
            f.write('include_directories({})\n'.format(dir))
        f.write('link_directories(bin)\n')
        f.write(
            'link_directories(D:/ProgramData/Anaconda3/libs)\n')  # 还要把python的inlcude文件夹添加进来，因为有可能和python交互，用到python36.lib
        for dir in set(slibFolder):
            dir = dir.replace('\\', '/')
            f.write('include_directories({})\n'.format(dir))
        f.write(str_)  # add_executable信息
        str1_ = 'TARGET_LINK_LIBRARIES({}'.format(projectName) + ' \n'
        for lib in set(sLIB):
            lib = lib.replace('\\', '/')
            str1_ += lib + '\n'
        str1_ += 'python36.lib' + '\n'  # 添加这个东西
        str1_ += 'imagehlp.lib' + '\n'  # 添加这个东西
        str1_ += ')\n'
        f.write('{}'.format(str1_))
        str1_ = 'TARGET_LINK_LIBRARIES({}'.format(projectName) + ' \n'
        for dll in set(sDLL):
            dll = dll.replace('\\', '/')
            if 'libtbb' not in dll:
                str1_ += dll + '\n'
        str1_ += ')\n'
        f.write('{}'.format(str1_))
    return 0


def findEffectiveLocOfSign(sign, str_, startLoc):
    # print(str_)
    # print('------------------------')
    loc = str_.find(sign, startLoc)
    if loc == -1:
        return -1
    unEffectiveCase1 = (str_[loc - 1] == '\\')
    locOfPreLinefeed = str_.rfind('\n', 0, loc)  # 最近的换行符位置
    locOfPreAnnotation = str_.rfind('//', 0, loc)  # 最近的注释位置
    if locOfPreLinefeed == -1:  # 此时是第一行，前面无换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            unEffectiveCase2 = True  # 属于无效位置
        else:
            unEffectiveCase2 = False
    else:  # 前面有换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            if locOfPreAnnotation > locOfPreLinefeed:  # 属于无效位置
                unEffectiveCase2 = True
            else:
                unEffectiveCase2 = False
        else:
            unEffectiveCase2 = False  # 属于有效位置
    if unEffectiveCase1 == False and unEffectiveCase2 == False:
        return loc
    else:  # 说明是无效位置，还要继续找
        loc = findEffectiveLocOfSign(sign, str_, loc + 1)
    return (loc)


def getRidOfTextBetweenDoubleQuote(str_):
    # find first有效位置
    sign = '\"'
    loc = findEffectiveLocOfSign(sign, str_, 0)
    if loc == -1:
        result = str_
        return (str_)
    else:
        loc2 = findEffectiveLocOfSign(sign, str_, loc + 1)
        str_ = str_.replace(str_[loc:loc2 + 1], '')
        str_ = getRidOfTextBetweenDoubleQuote(str_)
        return (str_)


def getRidOfTextBetweenSingleQuote(str_):
    # find first有效位置
    sign = '\''
    loc = findEffectiveLocOfSign(sign, str_, 0)
    if loc == -1:
        result = str_
        return (str_)
    else:
        loc2 = findEffectiveLocOfSign(sign, str_, loc + 1)
        str_ = str_.replace(str_[loc:loc2 + 1], '')
        str_ = getRidOfTextBetweenDoubleQuote(str_)
        return (str_)


def findEffectiveLocOfLeftBrace(str_, startLoc):  # 查找有效左大括号位置
    sign = '{'
    loc = str_.find(sign, startLoc)
    if loc == -1:
        return -1
    locOfPreLinefeed = str_.rfind('\n', 0, loc)  # 最近的换行符位置
    locOfPreAnnotation = str_.rfind('//', 0, loc)  # 最近的注释位置
    if locOfPreLinefeed == -1:  # 此时是第一行，前面无换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            unEffectiveCase2 = True  # 属于无效位置
        else:
            unEffectiveCase2 = False
    else:  # 前面有换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            if locOfPreAnnotation > locOfPreLinefeed:  # 属于无效位置
                unEffectiveCase2 = True
            else:
                unEffectiveCase2 = False
        else:
            unEffectiveCase2 = False  # 属于有效位置
    if unEffectiveCase2 == False:
        return loc
    else:  # 说明是无效位置，还要继续找
        loc = findEffectiveLocOfSign(sign, str_, loc + 1)
    return (loc)


def findEffectiveLocOfRightBrace(str_, startLoc):  # 查找有效左大括号位置
    sign = '}'
    loc = str_.find(sign, startLoc)
    if loc == -1:
        return -1
    locOfPreLinefeed = str_.rfind('\n', 0, loc)  # 最近的换行符位置
    locOfPreAnnotation = str_.rfind('//', 0, loc)  # 最近的注释位置
    if locOfPreLinefeed == -1:  # 此时是第一行，前面无换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            unEffectiveCase2 = True  # 属于无效位置
        else:
            unEffectiveCase2 = False
    else:  # 前面有换行符
        if locOfPreAnnotation != -1:  # 前面有注释符
            if locOfPreAnnotation > locOfPreLinefeed:  # 属于无效位置
                unEffectiveCase2 = True
            else:
                unEffectiveCase2 = False
        else:
            unEffectiveCase2 = False  # 属于有效位置
    if unEffectiveCase2 == False:
        return loc
    else:  # 说明是无效位置，还要继续找
        loc = findEffectiveLocOfSign(sign, str_, loc + 1)
    return (loc)


def getIndexOfCorreBrace(str_, locOfFirstLeftBrace, left_sign_counter, right_sign_counter):  # 查找对应右括号的位置
    # left_sign_counter = 1
    # right_sign_counter = 0
    locLeft = findEffectiveLocOfLeftBrace(str_, locOfFirstLeftBrace + 1)
    locRight = findEffectiveLocOfRightBrace(str_, locOfFirstLeftBrace + 1)
    if locRight == -1 and locLeft == -1:  # 全找不到
        raise ('原cpp文件有错，括号不成对儿')
    elif locRight == -1 and locLeft != -1:  #
        raise ('原cpp文件有错，括号不成对儿')
    elif locRight != -1 and locLeft == -1:  # 找得到右，找不到左
        right_sign_counter += 1
        if left_sign_counter == right_sign_counter:
            return (locRight)
        else:
            result = getIndexOfCorreBrace(str_, locRight, left_sign_counter, right_sign_counter)
            return (result)
    else:  # 左右全找的到
        # right_sign_counter+=1
        # left_sign_counter+=1
        if locRight < locLeft:
            right_sign_counter += 1
            if left_sign_counter == right_sign_counter:
                return (locRight)
            else:
                result = getIndexOfCorreBrace(str_, locRight, left_sign_counter, right_sign_counter)
                return (result)
        else:
            left_sign_counter += 1
            if left_sign_counter == right_sign_counter:  # 应该是不可能
                return (locRight)
            else:
                result = getIndexOfCorreBrace(str_, locLeft, left_sign_counter, right_sign_counter)
                return (result)


def getContentWithoutBrace(str_):  # 去掉{}当中的内容，template中的模板不许更新
    sData = str_.split('\n')
    recursiveMark = False
    lastline = ''
    lineLen = 0
    lineCounter = 0
    for line in sData:
        # 1 同一行包括'namespace'或'class'且包括'{' 这样括号间的内容不可删除
        # 2 本行虽然没有'namespace'或'class'，且本行包括'{'，但上一行包括'namespace'或'class',且上一行不含'{' 这样括号间的内容不可删除
        condition1 = (('namespace' in line) or ('class' in line) or ('template' in line)) and ('{' in line)
        condition2 = ((('namespace' not in line) and ('class' not in line) and (('template' not in line))) and (
                    '{' in line) and
                      (('namespace' in lastline) or ('class' in lastline) or ('template' in lastline)) and (
                                  '{' not in lastline))
        if condition1 or condition2:  # 不可删除，看下一行
            pass
        else:
            indexOfleftBrace = line.find('{')
            if indexOfleftBrace != -1:  # 找到了，那么就可以删除
                recursiveMark = True
                indexOfStr = indexOfleftBrace + lineLen + lineCounter
                endloc = getIndexOfCorreBrace(str_, indexOfStr, 1, 0)
                str_ = str_.replace(str_[indexOfStr:endloc + 1], ';')
                break
        lineCounter += 1
        lineLen += len(line)
        lastline = line
    if not recursiveMark:
        return (str_)
    else:
        return (getContentWithoutBrace(str_))


def reWriteThisCPPFile(sourceFilePath):
    with open(sourceFilePath, 'r', encoding='utf-8')as f:
        datas = f.readlines()
    sData = [line for line in datas if '#include' not in line]
    print(sourceFilePath.split('\\'))
    headerName = sourceFilePath.split('\\')[-1].replace('.cpp', '.h')
    str_ = '#include"{}"\n'.format(headerName)
    str_ = str_ + "".join(sData)
    with open(sourceFilePath, 'w', encoding='utf-8')as f:
        f.write(str_)


def tell_if_is_templateFile(filepath):
    with open(filepath, 'r', encoding='utf-8')as f:
        sData = f.readlines()
    templateMark = False
    for line in sData:
        if line.strip():
            if ('template' in line):
                if line.find('//') == -1:  # 模板关键字并不在注释中
                    templateMark = True
                    break
                elif line.find('template') < line.find('//'):  # 模板关键字并不在注释中
                    templateMark = True
                    break
    return (templateMark)


def getHPPFileContent(filepath):
    with open(filepath, 'r', encoding='utf-8')as f: datas = f.readlines()
    sData = [line for line in datas if '#include' not in line]
    sInclude_str = [line for line in datas if '#include' in line]
    str_ = "".join(sData)
    # str_ = getRidOfTextBetweenDoubleQuote(str_)  # 去掉正文中的小括号
    # str_ = getRidOfTextBetweenSingleQuote(str_).strip()
    str_ = getContentWithoutBrace(str_)  # 去掉非模板方法
    str_include = "".join(sInclude_str) + '\n'
    str_ = str_include + str_
    return (str_)


def removeTemplate(str_):  # 针对cpp
    sData = str_.split('\n')
    recursiveMark = False
    lastline = ''
    lineLen = 0
    lineCounter = 0
    for line in sData:
        # 1 同一行包括'namespace'或'class'且包括'{' 这样括号间的内容不可删除
        # 2 本行虽然没有'namespace'或'class'，且本行包括'{'，但上一行包括'namespace'或'class',且上一行不含'{' 这样括号间的内容不可删除
        condition1 = ('template' in line) and ('{' in line)
        condition2 = ('template' not in line) and ('{' in line) and ('template' in lastline) and ('{' not in lastline)
        if condition1 or condition2:  # 可以删除
            indexOfleftBrace = line.find('{')
            if indexOfleftBrace != -1:  # 找到了，那么就可以删除
                # 查找template t的位置
                indexOfTemplate = str_.rfind('template', indexOfleftBrace)
                recursiveMark = True
                indexOfStr = indexOfleftBrace + lineLen + lineCounter
                endloc = getIndexOfCorreBrace(str_, indexOfStr, 1, 0)
                # str_ = str_.replace(str_[indexOfStr:endloc + 1], ';')
                str_ = str_.replace(str_[indexOfTemplate:endloc + 1], ';')
                break
        else:  # 不可以删除
            pass
        lineCounter += 1
        lineLen += len(line)
        lastline = line
    if not recursiveMark:
        return (str_)
    else:
        return (getContentWithoutBrace(str_))


def getHFileContent(filepath):
    with open(filepath, 'r', encoding='utf-8')as f: datas = f.readlines()
    sData = [line for line in datas if '#include' not in line]
    sInclude_str = [line for line in datas if '#include' in line]
    str_ = "".join(sData)
    # str_ = getRidOfTextBetweenDoubleQuote(str_)  # 去掉正文中的小括号
    # str_ = getRidOfTextBetweenSingleQuote(str_).strip()
    str_ = getContentWithoutBrace(str_)
    str_include = "".join(sInclude_str) + '\n'
    str_ = str_include + str_
    return (str_)


def adjustCPPfile(filepath):  # remove template lines
    with open(filepath, 'r', encoding='utf-8')as f: datas = f.readlines()
    sData = [line for line in datas if '#include' not in line]
    str_ = "".join(sData)
    str_ = removeTemplate(str_)
    filename = filepath[filepath.rfind('\\') + 1:]
    filename = filename.replace('.cpp', '.hpp')
    str_ = "#include <{}>\n".format(filename) + str_
    with open(filepath, 'w', encoding='utf-8')as f:
        f.write(str_)


def autoReplenishFile(sSrcFile):
    s = sys.argv
    projectDir = s[1]
    projectName = projectDir.split('\\')[-1]
    # 检查所有源文件是否有对应的头文件
    for file in set(sSrcFile):
        if 'main.cpp' not in file:
            # 1判断其对应的头文件是否存在
            corresponding_header1 = file.replace('src', 'include').replace('.cpp', '.h')
            corresponding_header2 = file.replace('src', 'include').replace('.cpp', '.hpp')
            if (os.path.isfile(corresponding_header1) == False) and (os.path.isfile(corresponding_header2) == False):
                # 此时可知其对应头文件不存在，应该自动补头文件
                # 2判断源文件中，是否包含template字段，且template字段不在注释中，
                # 如果包含那么就全部复制到HPP文件
                if tell_if_is_templateFile(file):
                    print(file, 'template')
                    # 若为真，那么全部复制进新的hpp文件
                    fileName = corresponding_header2.split('\\')[-1].replace('.hpp', '')
                    sfolder = corresponding_header2.split('\\')
                    s = []
                    for folder in sfolder:
                        s.extend(folder.split('/'))
                    sFolder = s
                    sFolder = sFolder[sFolder.index(projectName):-1]
                    try:
                        os.makedirs("\\".join(corresponding_header2.split('\\')[:-1]))
                    except:
                        pass
                    with open(corresponding_header2, 'w', encoding='utf-8')as f:
                        str_ = '#ifndef '
                        for folder in sFolder:
                            str_ += folder.upper() + '_'
                        str_ += fileName.upper()
                        str_ += '_H\n'
                        f.write(str_)

                        str_ = '#define '
                        for folder in sFolder:
                            str_ += folder.upper() + '_'
                        str_ += fileName.upper()
                        str_ += '_H\n'
                        f.write(str_)

                        f.write(getHPPFileContent(file))

                        str_ = '\n#endif'
                        f.write(str_)
                    # 把源文件标志为弃用
                    # with open(file, 'w')as f:
                    #     f.write('//OriginSrcFile contain template,deprecated')
                    adjustCPPfile(file)
                    # sSrcFile.remove(file)
                else:  # 这个时候不含tempalte，采用正常的分离模式
                    print(file, 'withouttemplate')

                    fileName = corresponding_header1.split('\\')[-1].replace('.h', '')
                    sfolder = corresponding_header1.split('\\')
                    s = []
                    for folder in sfolder:
                        s.extend(folder.split('/'))
                    sFolder = s
                    sFolder = sFolder[sFolder.index(projectName):-1]
                    if not os.path.isdir(
                            corresponding_header1[:corresponding_header1.index(corresponding_header1.split('\\')[-1])]):
                        try:
                            os.makedirs(corresponding_header1[
                                        :corresponding_header1.index(corresponding_header1.split('\\')[-1])])
                        except:
                            pass

                    with open(corresponding_header1, 'w', encoding='utf-8')as f:
                        str_ = '#ifndef '
                        for folder in sFolder:
                            str_ += folder.upper() + '_'
                        str_ += fileName.upper()
                        str_ += '_H\n'
                        f.write(str_)

                        str_ = '#define '
                        for folder in sFolder:
                            str_ += folder.upper() + '_'
                        str_ += fileName.upper()
                        str_ += '_H\n'
                        f.write(str_)

                        f.write(getHFileContent(file))

                        str_ = '\n#endif'
                        f.write(str_)
                    reWriteThisCPPFile(file)  # 改头（把原来的include，变为include.h）
    return 0


def pushShutcut():
    time.sleep(1)
    win32api.keybd_event(16, 0, 0, 0)  # shift
    win32api.keybd_event(121, 0, 0, 0)  # f10
    time.sleep(0.1)
    win32api.keybd_event(16, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键
    win32api.keybd_event(121, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键


def examinFolder():
    sDLL=[]
    sSrcFile = []
    sLIB = []
    sInclude = []
    slibFolder = []
    sIncludefolder = []
    s = sys.argv
    x, projectFiledir, filedir = s
    projectName = projectFiledir[projectFiledir.rfind('\\') + 1:]
    # 找出项目绝对路径
    ab_dir = s[1]
    findAllSrcFile(ab_dir + '/src/*',sSrcFile)
    findAllSrcFile(ab_dir + '/MyTool/src/*',sSrcFile)
    findAllSrcFile('E:/CLionProjects/MYtoolTest/MyTool/src/*',sSrcFile)
    findAllSrcFile('E:/CLionProjects/MYtoolTest/src/simdjson/*',sSrcFile)

    findALLLibFile(ab_dir + '/bin/*',sLIB,slibFolder)
    findALLLibFile('E:\CLionProjects\MYtoolTest/bin/*',sLIB,slibFolder)

    findALLDllFile(ab_dir + '/bin/*',sDLL)
    findALLDllFile('E:\CLionProjects\MYtoolTest/bin/*',sDLL)

    findALLIncludeFile(ab_dir + '/MyTool/include/*',sInclude,sIncludefolder)
    findALLIncludeFile(ab_dir + '/include/*',sInclude,sIncludefolder)
    findALLIncludeFile('E:\CLionProjects\MYtoolTest/include/*',sInclude,sIncludefolder)
    findALLIncludeFile('E:/CLionProjects/MYtoolTest/MyTool/include',sInclude,sIncludefolder)
    sIncludefolder.append('E:/CLionProjects/MYtoolTest/include')

    sSrcFile = list(set(sSrcFile))
    sLIB = list(set(sLIB))
    sDLL = list(set(sDLL))
    sInclude = list(set(sInclude ))
    slibFolder = list(set(slibFolder))
    sIncludefolder = list(set(sIncludefolder))

    print('项目源文件集合:', sSrcFile)
    print('项目动态库文件集合:', sDLL)
    print('项目静态库文件集合:', sLIB)
    print('项目头文件夹集合:', sInclude)
    print('项目库文件夹集合:', slibFolder)
    print('项目头文件夹集合:', sIncludefolder)
    return (ab_dir, projectName, sSrcFile, sDLL, sLIB, sInclude, slibFolder, sIncludefolder)


def examin_dll_src():
    sDLL = []
    sSrcFile = []

    s = sys.argv
    # 找出项目绝对路径
    ab_dir = s[1]

    findALLDllFile(ab_dir + '/bin/*',sDLL)
    findALLDllFile('E:\CLionProjects\MYtoolTest/bin/*',sDLL)
    sDLL = list(set(sDLL))

    findAllSrcFile(ab_dir + '/src/*', sSrcFile)
    findAllSrcFile(ab_dir + '/MyTool/src/*', sSrcFile)
    findAllSrcFile('E:/CLionProjects/MYtoolTest/MyTool/src/*', sSrcFile)
    findAllSrcFile('E:/CLionProjects/MYtoolTest/src/simdjson/*', sSrcFile)
    sSrcFile = list(set(sSrcFile))

    return (sDLL,sSrcFile)


def trytocopyQTdll(sDLL):
    s = sys.argv
    projectDir = s[1]
    # 查看是否存在cmake-build-debug文件夹  cmake-build-release文件夹
    path1 = projectDir + '/cmake-build-debug'
    path2 = projectDir + '/cmake-build-release'
    if not os.path.exists(path1):
        try:
            os.makedirs(path1)
        except:
            pass
    if not os.path.exists(path2):
        try:
            os.makedirs(path2)
        except:
            pass
    # 查看是否存在那些动态库
    for dll in sDLL:
        if not os.path.exists(path1 + '\\' + dll.split('/')[-1]):
            shutil.copy(dll, path1)
        if not os.path.exists(path2 + '\\' + dll.split('/')[-1]):
            shutil.copy(dll, path2)


def main():
    s = sys.argv
    projectDir = s[1]
    try:
        os.makedirs(projectDir + '/bin/')
    except:
        pass
    try:
        os.makedirs(projectDir + '/src/')
    except:
        pass
    try:
        os.makedirs(projectDir + '/include/')
    except:
        pass
    try:
        os.makedirs(projectDir + '/MyTool/include/')
    except:
        pass
    try:
        os.makedirs(projectDir + '/MyTool/src/')
    except:
        pass
    sDLL,sSrcFile=examin_dll_src()
    trytocopyQTdll(sDLL)
    autoReplenishFile(sSrcFile)
    ab_dir, projectName, sSrcFile, sDLL, sLIB, sInclude, slibFolder, sIncludefolder = examinFolder()
    WriteMake(ab_dir, projectName, sSrcFile, sDLL, sLIB, sInclude, slibFolder, sIncludefolder)
    return 0


main()
