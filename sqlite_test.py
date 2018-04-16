#!/usr/bin/env python
    
import sqlite3,re
    
class SQLDB():

    def __init__(self,db_name):
        self.db = sqlite3.connect(db_name)
    
    def select_all(self):
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
                        cursor.execute('Create table motion(id INTEGER PRIMARY KEY NOT NULL, name TEXT, state TEXT)')
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_motion','False')")
                    elif re.search('no such column:', str(e), re.I | re.M):
                        cursor.execute("Insert into motion (name, state) values('kill_camera','False')")
                        cursor.execute("Insert into motion (name, state) values('kill_motion','False')")
                    self.db.commit()

    def insert(self,column,value):
        with self.db:
            cursor = self.db.cursor()
            try:
                cursor.execute("insert into " + column + " values(" + value + ");")
            except Exception as e:
                pass
            self.db.commit()

    def update(self,column,value):
        with self.db:
            cursor = self.db.cursor()
            try:
                cursor.execute("update motion set state = '" + value + "' where name = '" + column + "';")
            except Exception as e:
                pass
            self.db.commit()

    def kill_camera_state(self):
        for d in self.select_all():
            if re.search('kill_camera', str(d["name"])):
                return d['state']

    def kill_motion_state(self):
        for d in self.select_all():
            if re.search('kill_camera', str(d["name"])):
                return d['state']

if __name__ == '__main__':
    sqldb = SQLDB('motiondetection.db')
    sqldb.select_all()
