import torndb
import os
import sys
import requests

SAVE_DIR='.'
con = torndb.Connection("120.27.92.166", "apk", user="root", password="112112")

finish_num = 0
fail_num = 0
log = open('log.txt', 'w')
def update(apk,state):
    try:
        sql = "UPDATE apk SET state = '%d' WHERE pacname = '%s'" %(state, apk['pacname'])
        con.update(sql)
    except Exception as e:
        log.write(e)


def downloader(apk):
    global finish_num
    global fail_num
    try:
        apk_url = apk['url']
        if not apk_url[0:4] == 'https':
            apk_url = 'https'+apk_url[4:]
        category = apk['category']
        save_dir=os.path.join(SAVE_DIR, category)
        filename = apk['name']
        save_path=os.path.join(save_dir, filename.strip()+'.apk')
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        #if (not os.path.exists(save_path)) or os.stat(save_path).st_size == 0:
        if os.path.exists(save_path):
            print ('downloading:' + apk_url + ' as: ' + save_path)
            result = requests.get(apk_url).content
/           file = open(save_path, 'wb+')
            file.write(result)
            file.flush()
            file.close()
            print ('download finish:'+apk_url+' as: '+save_path)
        else:
            print(save_path+'is exits')
        finish_num += 1
        update(apk, 1)
    except:
        etype, evalue, tracebackObj = sys.exc_info()[:3]
        log.write('url:%s errortype:%s errorvalue:%s' % (apk_url, etype, evalue))
        log.flush()
        fail_num += 1
        #update(apk, -1)

if __name__== '__main__':
    apks = con.query('select * from apk where state = 1 AND is_malware = 0')
    for apk in apks:
        downloader(apk)
    print ('finish: %d fail %d' %(finish_num,fail_num))
    print ('finish task')
    log.close()