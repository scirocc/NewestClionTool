
import sys
import os
import win32api
import win32con
import glob
import time


def getFile():
    s = sys.argv
    x, projectFiledir, fileParentdir,filename = s
    print(projectFiledir,fileParentdir,filename)
    return(projectFiledir,fileParentdir,filename)

def getNameSpace(projectFiledir,fileParentdir,filename):
    tailInfo=fileParentdir[len(projectFiledir):]
    s=tailInfo.split('\\')
    s=[folder for folder in s if folder]
    firstLine='namespace '

    for i,folder in enumerate(s):
        if i==0:
            firstLine+=folder
        else:
            firstLine+='::'
            firstLine+=folder
    firstLine+="{\n"
    lastLine='\n}'
    # with open(fileParentdir+'\\'+filename,'w',encoding='gbk')as f:
    #     f.write(firstLine)
    #     f.write(lastLine)
    return(firstLine,lastLine)

def writeInclude(fileParentdir,filename,firstLine,lastLine):


    with open(fileParentdir+'\\'+filename,'w',encoding='gbk')as f:
        f.write('#include<dictTrans.hpp>\n')
        f.write('#include<glob.h>\n')
        f.write('#include<ioStuff.hpp>\n')
        f.write('#include<jsonStuff.hpp>\n')
        f.write('#include<MultiThreadFrame.hpp>\n')
        f.write('#include<MySetStuff.hpp>\n')
        f.write('#include<MySlice.hpp>\n')
        f.write('#include<MySort.hpp>\n')
        f.write('#include<MySTLStuff.hpp>\n')
        f.write('#include<MyTimeStuff.hpp>\n')
        f.write('#include<strStuff.hpp>\n')


        f.write(firstLine)
        f.write(lastLine)



projectFiledir,fileParentdir,filename=getFile()
firstLine,lastLine=getNameSpace(projectFiledir,fileParentdir,filename)
writeInclude(fileParentdir,filename,firstLine,lastLine)