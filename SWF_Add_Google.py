# -*- coding: utf-8 -*-


import os, glob
def GetAllAsasm():
    files = []
    for asasm in glob.glob(GetPathByName("*")):
        files += [asasm]
    return files

def GetClassNameByFile(file):
    return file.replace("\\", "/").split("/")[-1].split('.')[0].replace("%", "\\x")
    
def GetPathByName(name):
    return "./158-0/{0}.class.asasm".format(name.replace("\\x", "%"))

    
def ReadAllLines(path):
    return ReadAllText(path).split('\n')
    
def ReadAllText(path):
    r = open(path.replace("\\x", "%"), encoding='utf-8')
    text = r.read()
    r.close()
    return text
    
def WriteAllLines(path, text):
    WriteAllText(path, "\n".join(map(str, text)))
    
def WriteAllText(path, text):
    w = open(path.replace("\\x", "%"), "w+")
    w.write(text)
    w.close()
    
def FindImgGoogle():
    find = 'pushstring          "x_transformice/x_interface/google/auth_google.png"'
    for file in files:
        lines = ReadAllLines(file)
        x = 0
        while x < len(lines):
            if find in lines[x]:
                return [lines[x-1].split('"')[3]]
            x+=1
    return []

    
def FindFile(a):
    find = 'getproperty         QName(PackageNamespace(""), "{0}")'.format(a[0])
    P1 = ""
    P22 = False
    P11 = False
    tmp = 'BBBBBBBBBBBBBBBBBBBBBB'
    for file in files:
        lines = ReadAllLines(file)
        x = 0
        if P22: break
        while x < len(lines):
            if find in lines[x]:
                P22 = True
                P1 = lines[x+1].split('"')[3]
                break
            x+=1
    if P22:
        find = 'constructprop       QName(PackageNamespace(""), "{0}")'.format(P1)
        for file in files:
            lines = ReadAllLines(file)
            x = 0
            if P11: break
            while x < len(lines):
                if find in lines[x]:
                    while not 'trait method' in lines[x]: x-=1
                    P11 = True
                    P1 = lines[x].split('"')[3]
                    break
                x+=1
    if P11:
        find = 'getproperty         QName(PackageNamespace(""), "{0}")'.format(P1)
        for file in files:
            lines = ReadAllLines(file)
            x = 0
            while x < len(lines):
                if find in lines[x]:
                    temp = lines[x-1].split('"')[3]
                    lines[x-3] = '     getlex              QName(PackageNamespace(""), "{0}")'.format(temp)
                    lines[x-2] = tmp
                    lines[x-1] = tmp
                    lines[x] = tmp
                    lines[x+1] = '     callpropvoid        QName(PackageNamespace(""), "{0}"), 0'.format(P1)
                    x+=2
                    while not 'callpropvoid' in lines[x]: x+=1
                    temp1 = lines[x-1].split('"')[3]
                    lines[x-3] = tmp
                    lines[x-2] = tmp
                    lines[x-1] = tmp
                    lines[x-4] = '     getlex              QName(PackageNamespace(""), "{0}")'.format(temp)
                    lines[x] = '     callpropvoid        QName(PackageNamespace(""), "{0}"), 0'.format(temp1)
                    while tmp in lines:
                        lines.remove(tmp)
                    WriteAllLines(file, lines)
                    return file
                x+=1
    return ""

if __name__ == "__main__":
    print("Started")
    P11 = False
    P22 = False
    files = GetAllAsasm()
    P1 = FindImgGoogle()
    if P1:
        P2 = FindFile(P1)
        if P2:
            print(P2)
            print("Finished")
    os.system("pause")