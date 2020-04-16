import os

def getLogListByTag(tag):
    dirname = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]
    if tag == "page":
        dirname = dirname+"/logs"
    elif tag == "backstage":
        dirname = dirname+"/compile/logs"
    return getLogList(dirname)

def getLogList(dirname,typeFilter=[".log"]):
    if not os.path.isdir(dirname) or not os.path.exists(dirname):
        return []
    result = []
    cnt = 1
    for maindir, subdir, file_name_list in os.walk(dirname,topdown=True):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename) #合并成一个完整路径
            ext = os.path.splitext(filename)[1]  # 获取文件后缀 [0]获取的是除了文件名以外的内容
            if ext in typeFilter:
                result.append({
                    "id_log":cnt,
                    "filename":filename,
                    "size":os.path.getsize(apath),
                    "path":apath
                })
                cnt += 1
    result.sort(key=accordingDate,reverse=True)
    idx = 1
    for item in result:
        item["id_log"] = idx
        idx += 1
    return result

def accordingDate(listTemp):
    return listTemp["filename"]

def readLog(filePath):
    if not os.path.isfile(filePath) or not os.path.exists(filePath):
        return {
            "content":""
        }
    content = ""
    with open(filePath, "r", encoding='UTF-8') as file:
        content = file.read()
    return {
            "content":content
        }

if __name__ == "__main__":
    getLogListByTag(tag="page")
    # readLogs(base_dir+"/Logs","")