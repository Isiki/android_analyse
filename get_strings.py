# coding: utf-8
import os
import torndb
import re
apkPath = "D:\\android\\apktool_out\\"
dirlist = os.listdir(apkPath)
con = torndb.Connection('120.27.92.166','apk',user='root',password='112112')


def getString(path):
    string = ''
    if os.path.exists(path):
        file = open(path, 'r')
        for line in file:
            pattern = re.compile("<string(.*)>(.*)</string>")
            res = pattern.search(line)
            if not res == None:
                rawstr = res.group(2)
                str = re.sub('[^a-zA-Z\s]'," ",rawstr)
                strs= str.split()
                for str in strs:
                    str = str.lstrip(',')
                    if not len(str)==1:
                        string+=str+','
    return string


def getPackage(path):
    file = open(path, 'r')
    for line in file:
        pattern = re.compile("package=(\S*)\"(.*)")
        res = pattern.search(line)
        if not res == None:
            package = res.group(1).split()[0]
            package = package.strip("\"")
            return package
    return ''


for i in range(1,len(dirlist)):  # 得到apk 文件夹下的每一个子的类别
    filelist = apkPath + dirlist[i]  # 获取每个类别的路径
    apklist = os.listdir(filelist)  # 获取每个路径下的apk 列表
    for APK in apklist:
        path = filelist+'\\'+APK+'\\AndroidManifest.xml'
        package = ''
        if os.path.exists(path):
            package = getPackage(path)
        path = filelist+'\\'+APK+'\\res\\'
        if os.path.exists(path):
            stringpath = os.listdir(path)
            string = ''
            for dir in stringpath:
                if dir[:6]=='values':
                    path += dir+'\\strings.xml'
                    string+=getString(path)
            con.execute("update apk_permission set string='%s' where package='%s'"%(string,package))
    print dirlist[i]+' done'
con.close()
print "all work done"

