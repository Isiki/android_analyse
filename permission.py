#coding: utf-8
import torndb
import os
con = torndb.Connection('120.27.92.166','apk',user='root',password='112112')

file = open('./permission list.csv','r')
# for line in file:
#     con.insert('insert into permission_list(name) VALUE(%s)',line.strip('\n'))
sql = "create table new_apk_permission()"
con.close()