#!/usr/bin/env python
    
import sqlite3,re
    
class SQLDB():
    
    def selectAll(self):
        db = sqlite3.connect('test.db')
        while True:
            with db:
                db.row_factory = sqlite3.Row
                cursor = db.cursor()
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
                    db.commit()

if __name__ == '__main__':
    sqldb = SQLDB()
    for d in sqldb.selectAll():
        print "%s %s %s " % (d["id"], d["name"], d["state"])
