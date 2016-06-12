#coding:utf-8
import argparse

from androguard.misc import *
from androguard.core.bytecodes.apk import *
import sys
import multiprocessing
import torndb
PERMISSIONS={}
db=torndb.Connection("120.27.92.166","apk",user="root",password="112112")


def extract_apk_permisson(name,category):
    path = '/media/isiki/本地磁盘/android/crawler/weather'+category+'/'+name
    try:
        apk=APK(path.encode('utf-8'))
        if apk.is_valid_APK():
            package=apk.get_package()
            permissions=apk.get_permissions()
            # clean repeat permission
            simple_permissions=set()
            for p in permissions:
                p=p.split('.')[-1]
                if PERMISSIONS.has_key(p):
                    simple_permissions.add(p)

            insert_sql='insert into apk_permission(package,isMalware'
            attrs=','

            for permission in simple_permissions:
                    attrs=attrs+permission+','

            attrs=attrs.rstrip(',')
            values="values ('%s',%d,"%(package,1)
            for i in range(len(simple_permissions)):
                values=values+'1,'
            values=values.rstrip(',')
            values=values+')'

            insert_sql=insert_sql+attrs+') '+values

            print insert_sql
            db.insert(insert_sql)

            print ('analysis %s'%(path))
        else:
            print('%s is not valid apk'%(path))
    except:

        etype, evalue, tracebackObj = sys.exc_info()[:3]
        print ('apk:%s errortype:%s errorvalue:%s'%(path,etype,evalue))
    finally:
        db.update("update apk set is_malware=1 where name='%s'"%name)

def get_permissions():
    global PERMISSIONS
    sql='select * from permission'

    result=db.query(sql)
    PERMISSIONS={ item['name']:{'protectionLevel':item['protectionLevel'],'permissionGroup':item['permissionGroup']} for item in result }

def get_un_analysis_files():
    sql='select name,category from apk WHERE is_malware=0'
    result=db.query(sql)
    return result

def mutil_process_analysis():
    pool=multiprocessing.Pool(processes=args.process)
    files=get_un_analysis_files()
    path = '/media/isiki/本地磁盘/android/crawler/'
    for file in files:
        pool.apply(extract_apk_permisson,(file['name'],file['category']))
    pool.close()
    pool.join()
    print('finish work')

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--process", default=30,type=int,
                        help="process number")
    args=parser.parse_args()
    get_permissions()

    #mutil_process_analysis()
    extract_apk_permisson('WEATHER RADAR 0.1.apk','weather')


