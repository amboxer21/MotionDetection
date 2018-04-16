#!/usr/bin/env python
    
import sqlite3,re
    
class SQLDB():

    def __init__(self,db_name):
        self.db = sqlite3.connect(db_name)
    
    def selectAll(self):
        while True:
            with self.db:
                self.db.row_factory = sqlite3.Row
                cursor = self.db.cursor()
                try:
                    cursor.execute('select * from motion')
                    data = cursor.fetchall()
                    return data
                except sqlite3.OperationalError as e:
                    if re.search('no such table:', str(e), re.I | re.M):
                        print("Exception e => " + str(e))
                        cursor.execute('Create table motion(id INTEGER PRIMARY KEY NOT NULL, name TEXT, state TEXT)')
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_motion','False')")
                    elif re.search('no such column:', str(e), re.I | re.M):
                        print("Exception e => " + str(e))
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_motion','False')")
                    self.db.commit()

    def killCamera(self):
        for d in self.selectAll():
            if re.search('kill_camera', str(d["name"])):
                return d['state']

    def killMotion(self):
        for d in self.selectAll():
            if re.search('kill_camera', str(d["name"])):
                return d['state']

if __name__ == '__main__':
    sqldb = SQLDB('test.db')
    sqldb.selectAll()
    print "killCamera() => " + str(sqldb.killCamera())
    for d in sqldb.selectAll():
        print "%s %s %s" % (d["id"], d["name"], d["state"])
