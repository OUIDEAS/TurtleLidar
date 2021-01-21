import sqlite3
from sqlite3 import Error
import time
from datetime import datetime
import csv
import pickle
import bz2
import io
import zipfile
import os
import LidarPlot

class TurtleLidarDB:
    def __enter__(self, db_file="LidarData.db"):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        except Error as e:
            print(e)

        exists = self.check_lidar_data_table_exists()
        if(exists == False):
            print("creating lidar data table")
            self.create_lidar_table()

        exists = self.check_lidar_status_table_exists()
        if(exists == False):
            print("creating lidar status table")
            self.create_LidarStatus_table()

        exists = self.check_polarplots_table_exists()
        if(exists == False):
            print("creating poloar plot table")
            self.create_polarplot_table()

        return self

    def create_lidar_table(self):
        #self.insert_debug_msg("create_lidar_table")
        create_table_sql = """CREATE TABLE IF NOT EXISTS LidarData (
                                            id integer PRIMARY KEY,
                                            timestamp REAL NOT NULL,
                                            odometer blob,
                                            lidar blob,
                                            avgR REAL,
                                            stdR REAL,
                                            minR REAL,
                                            maxR REAL,
                                            xCenter REAL,
                                            yCenter REAL,
                                            gyro blob,
                                            Image blob,
                                            batVolt REAL,
                                            Deleted TEXT
                                        );"""

        try:
            self.c.execute(create_table_sql)
            self.conn.commit()
        except Error as e:
            print("error: create_lidar_table" + str(e))
            self.insert_debug_msg(e)

    def check_polarplots_table_exists(self):
        return self.check_table_exists("PolarPlots")

    def check_table_exists(self, name):
        exists = False
        try:
            self.c.execute('''SELECT id FROM %s''' % name)
            data = self.c.fetchall()
            exists = True
        except sqlite3.OperationalError as e:
            exists = False

        return exists

    def check_lidar_data_table_exists(self):
        exists = False
        try:
            self.c.execute('''SELECT id FROM LidarData''')
            data = self.c.fetchall()
            exists = True
        except sqlite3.OperationalError as e:
            exists = False

        return exists
            
    def check_debug_table_exists(self):
        exists = False

        try:
            self.c.execute("""SELECT id FROM DebugData""")
            data = self.c.fetchall()
            #print(data)
            exists = True
        except sqlite3.OperationalError as e:
            #print("error: check_debug_table_exists")
            #print(e)
            #does not EXIST
            exists = False

        return exists

    def create_debug_table(self):
        create_table_sql = """CREATE TABLE IF NOT EXISTS DebugData (
                                            id integer PRIMARY KEY,
                                            timestamp REAL NOT NULL,
                                            debugdata TEXT
                                        );"""
        try:
            self.c.execute(create_table_sql)
            self.conn.commit()
        except Error as e:
            print("error: create_debug_table")
            print(e)
            return -1
        return 0

    def get_all_debug_msg(self):
        selectsql = '''SELECT * FROM DebugData '''
        seldata = None
        try:
            seldata = self.c.execute(selectsql)
        except Error as e:
            print("Select all error with debug msg " + e)
            return None

        return seldata.fetchall()

    def get_last_n_debug_msg(self,numsel):
        selectsql = '''SELECT * FROM DebugData ORDER BY ID DESC LIMIT ?;'''
        try:
            data = (numsel, )
            seldata = self.c.execute(selectsql, data)
            newdata = []
            alldata = seldata.fetchall()
            for i in range(len(alldata), 0, -1):
                newdata.append(alldata[i-1])
            seldata = newdata
        except Error as e:
            print("Select last n error with debug msg " + e)
            return None

        return seldata

    def check_and_create_debug_table(self):
        if not self.check_debug_table_exists():
            self.create_debug_table()

        if not self.check_debug_table_exists():
            print("Tried to create debug DB and failed...")
            return -1
        return 0

    def get_new_debug_msg_from_ID(self,lastID):
        if(self.check_and_create_debug_table() == -1):
            return None

        selectsql = '''SELECT * FROM DebugData WHERE ID > ? ORDER BY ID ASC LIMIT 100;'''
        try:
            data = (lastID, )
            seldata = self.c.execute(selectsql, data)
        except Error as e:
            print("Select last n error with debug msg " + e)
            return None

        return seldata.fetchall()

    def insert_debug_msg(self, msg):
        if not self.check_debug_table_exists():
            self.create_debug_table()

        if not self.check_debug_table_exists():
            print("Tried to create debug DB and failed...")
            return -1

        insertsql = '''INSERT INTO DebugData (timestamp, debugdata) VALUES(?,?) '''
        if isinstance(msg, str):
            data = (time.time(), msg)
            self.c.execute(insertsql, data)
            self.conn.commit()
        else:
            print("Insert error with debug msg " + msg)
            return -1

        return 0

    def create_polarplot_table(self):
        create_table_sql = """CREATE TABLE IF NOT EXISTS PolarPlots (
                                            id integer PRIMARY KEY,
                                            lidarid integer,
                                            polarimage blob
                                        );"""
        try:
            self.c.execute(create_table_sql)
            self.conn.commit()
        except Error as e:
            print("error: create_polarplot_table")
            print(e)
            return -1
        return 0

    def get_polarplot_by_lidarID(self, lidarID):
        self.insert_debug_msg("get_table_data")
        self.c.execute("SELECT * FROM PolarPlots WHERE lidarid=?", (lidarID,))

        rows = self.c.fetchall()
        if not rows:
            plotdata = None
        else:
            row = rows[0]
            plotdata = pickle.loads(row[2])

        return plotdata

    def insert_polarplot(self, img, lidarID):
        if not self.check_polarplots_table_exists():
            self.create_polarplot_table()

        if not self.check_polarplots_table_exists():
            print("Tried to create polar plot table and failed...")
            return -1

        Image = pickle.dumps(img)

        insertsql = '''INSERT INTO PolarPlots (lidarid, polarimage) VALUES(?,?) '''
        if isinstance(lidarID, int):
            data = (lidarID, Image)
            self.c.execute(insertsql, data)
            self.conn.commit()
        else:
            print("Insert error with polar plot" + str(lidarID))
            return -1

        return 0

    def create_LidarStatus_table(self):
        self.insert_debug_msg("create_LidarStatus_table")
        if(self.check_lidar_status_table_exists()):
            return 0

        create_table_sql = """CREATE TABLE IF NOT EXISTS LidarStatus (
                                            id integer PRIMARY KEY,
                                            timestamp REAL NOT NULL,
                                            status TEXT,
                                            battery_voltage REAL
                                        );"""

        try:
            self.c.execute(create_table_sql)
            self.conn.commit()
            self.c.execute('''SELECT id FROM LidarStatus''')
            rows = self.c.fetchall()
            if not rows:
                sql = ''' INSERT INTO LidarStatus (timestamp, status, battery_voltage)
                                      VALUES(?,?,?) '''
                data = (time.time(), "Loading...", 0.0)
                self.c.execute(sql, data)
                self.conn.commit()
            else:
                self.update_lidar_status("Loading...")
        except Error as e:
            self.insert_debug_msg(e)
            return -1
        return 0



    def update_lidar_status(self, msg=None, battery_voltage=-1):
        self.insert_debug_msg("update_lidar_status")

        sql_xtra = ""
        if(battery_voltage >= 0 and msg):
            sql_xtra = "status = ?, battery_voltage = ?"
            data = (time.time(), msg, battery_voltage, 1)
        elif(battery_voltage < 0 and msg):
            sql_xtra = "status = ?"
            data = (time.time(), msg, 1)
        elif(battery_voltage >=0 and not msg):
            sql_xtra = "battery_voltage = ?"
            data = (time.time(), battery_voltage, 1)
        else:
            #why would you do this?
            return None

        #sql = "UPDATE LidarStatus SET timestamp = 42, status = 'hello-', battery_voltage = 4 WHERE id = 1;"

        sql = "UPDATE LidarStatus SET timestamp = ?, " + sql_xtra + " WHERE id = ?"
        self.c.execute(sql, data)
        #self.c.execute(sql, data)
        #self.conn.commit()

        return self.c.lastrowid

    def check_lidar_status_table_exists(self):
        exists = False
        try:
            self.c.execute('''SELECT id,timestamp, status FROM LidarStatus''')
            data = self.c.fetchall()
            #print(data)
            exists = True
        except sqlite3.OperationalError as e:
            #print("check_lidar_status_table_exists -> " + str(e))
            exists = False

        return exists

    def get_lidar_status(self):
        #self.insert_debug_msg("get_lidar_status")

        message = ""
        try:
            self.c.execute('''SELECT id,timestamp,status,battery_voltage FROM LidarStatus''')
            rows = self.c.fetchall()
            message = rows[0][2]
            battery = rows[0][3]
            if(not battery):
                battery = -1
            #print(rows)
        except Error as e:
            self.insert_debug_msg(e)

        return message, battery

    def insert_lidar_data(self, Time, odo, lidar, avgR, stdR, minR, maxR, xCenter, yCenter, gyro, image, batVolt):
        self.insert_debug_msg("create_lidar_data_input")

        # lidar = tuple(zip(angle, radius))
        Lidar = pickle.dumps(lidar)
        LIDAR = bz2.compress(Lidar)
        Gyro = pickle.dumps(gyro)
        # GYRO = bz2.compress(Gyro)
        Image = pickle.dumps(image)
        # IMAGE = bz2.compress(Image)
        ODO = pickle.dumps(odo)

        sql = ''' INSERT INTO LidarData (timestamp,odometer,lidar,avgR,stdR,minR,maxR,xCenter,yCenter,gyro,Image, batVolt, Deleted)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''

        # cur = conn.cursor()
        # for item in range(len(radius)):
        de = "False"
        data = (Time, ODO, LIDAR, avgR, stdR, minR, maxR, xCenter, yCenter, Gyro, Image, batVolt, de)
        self.c.execute(sql, data)
        self.conn.commit()
        return self.c.lastrowid

    def get_all_lidar_data(self):
        self.insert_debug_msg("get_table_data")

        self.c.execute('''SELECT id,timestamp,odometer, avgR, stdR, minR, maxR, xCenter, yCenter, batVolt FROM LidarData''')
        rows = self.c.fetchall()
        out = []
        for row in rows:
            row = list(row)
            o = pickle.loads(row[2])
            if type(o) is tuple:
                row[2] = (o[0] + o[1] + o[2] + o[3])/4
            else:
                row[2] = 0
            out.append(row)
        return out

    def get_lidar_data_byID(self, rowID=1):
        self.insert_debug_msg("get_table_data")
        self.c.execute("SELECT * FROM LidarData WHERE id=?", (rowID,))

        rows = self.c.fetchall()
        if not rows:
            LidarData = None
        for row in rows:

            LidarData = {
                "Lidar": pickle.loads(bz2.decompress(row[3])),
                "Time": row[1],
                # "odo": row[2],
                "odo": pickle.loads(row[2]),
                "AvgR": row[4],
                "StdRadius": row[5],
                "minR": row[6],
                "maxR": row[7],
                "xCenter": row[8],
                "yCenter": row[9],
                # "gyro": pickle.loads(bz2.decompress(row[10])),
                "gyro": pickle.loads(row[10]),
                # "image": pickle.loads(bz2.decompress(row[11]))
                "image": pickle.loads(row[11]),
                "bat": row[12]
            }

            # print(LidarData)
        return LidarData

    def delete_lidar_data(self, RowID):
        self.insert_debug_msg("delete_lidar_data")

        """
        update priority, begin_date, and end date of a task
        :param conn:
        :param task:
        :return: project id
        """
        sql = ''' UPDATE LidarData
                  SET Deleted = ?
                  WHERE id = ?'''

        data = ("True", RowID)
        self.c.execute(sql, data)
        self.conn.commit()

    def get_all_lidar_ids(self):
        self.c.execute('''SELECT id FROM LidarData''')
        rows = self.c.fetchall()
        return rows

    def create_csv_zip_bytes(self):
        self.insert_debug_msg("create_csv")

        rows = self.get_all_lidar_ids()
        k = max(rows)

        ImageData = {}
        LidarData = {}
        for i in range(k[0]):
            data = self.get_lidar_data_byID(i+1)
            dt = datetime.fromtimestamp(data['Time'])
            date_time = dt.strftime("%m-%d-%Y_%H.%M.%S")
            LidarData[date_time] = io.StringIO()
            ImageData[date_time] = data["image"]

            writer = csv.writer(LidarData[date_time], dialect='excel', delimiter=',')
            writer.writerow(['Angle', 'Range', 'Time', 'AvgR', 'StdR', 'minR', 'maxR', 'xCenter', 'yCenter', 'Odometer',
                             'eulerX', 'eulerY', 'eulerZ', 'gyroX', 'gyroY', 'gyroZ', 'accX', 'accY', 'accZ', 'magX', 'magY', 'magZ',
                             'BatVolt'])
            FirstRow = [data["Lidar"][0][0], data["Lidar"][0][1], data['Time'], data["AvgR"], data['StdRadius'],
                        data["minR"], data['maxR'], data['xCenter'], data['yCenter'], data["odo"],
                        data["gyro"][0][0], data["gyro"][0][1], data["gyro"][0][2],
                        data["gyro"][1][0], data["gyro"][1][1], data["gyro"][1][2],
                        data["gyro"][2][0], data["gyro"][2][1], data["gyro"][2][2],
                        data["gyro"][3][0], data["gyro"][3][1], data["gyro"][3][2], data["bat"]]
            writer.writerow(FirstRow)
            writer.writerows(data["Lidar"][1:])

        zip_file = io.BytesIO()
        with zipfile.ZipFile(zip_file, 'w') as zf:
            for file in LidarData:
                filename = file + '.csv'
                zipdata = zipfile.ZipInfo(filename)
                zipdata.compress_type = zipfile.ZIP_BZIP2
                zipdata.date_time = time.localtime(time.time())[:6]
                zf.writestr(zipdata, LidarData[file].getvalue())

                if ImageData[file] is not None and ImageData[file] != 'Image':
                    filename = file + '.JPEG'
                    zipdata = zipfile.ZipInfo(filename)
                    zipdata.compress_type = zipfile.ZIP_BZIP2
                    zipdata.date_time = time.localtime(time.time())[:6]
                    zf.writestr(zipdata, ImageData[file])

        zip_file.seek(0)
        return zip_file

    def create_csv_zip(self, filename='LidarData.zip'):
        csvbytes = self.create_csv()
        with open(filename, "wb") as f:  ## Excel File
            f.write(csvbytes.getbuffer())
        # self.insert_debug_msg("create_csv_zip")
        #
        # self.c.execute('''SELECT id FROM LidarData''')
        # rows = self.c.fetchall()
        # k = max(rows)
        #
        # LidarData = {}
        # for i in range(k[0]):
        #     data = self.get_lidar_data(i + 1)
        #     dt = datetime.fromtimestamp(data['Time'])
        #     date_time = dt.strftime("%m-%d-%Y_%H.%M.%S")
        #     LidarData[date_time] = io.StringIO()
        #
        #     writer = csv.writer(LidarData[date_time], dialect='excel', delimiter=',')
        #     writer.writerow(['Angle', 'Range', 'Time', 'AvgR', 'StdR', 'minR', 'maxR', 'xCenter', 'yCenter', 'Odometer',
        #                      'eulerX', 'eulerY', 'eulerZ', 'gyroX', 'gyroY', 'gyroZ', 'accX', 'accY', 'accZ', 'magX', 'magY', 'magZ',
        #                      'BatVolt'])
        #     FirstRow = [data["Lidar"][0][0], data["Lidar"][0][1], data['Time'], data["AvgR"], data['StdRadius'],
        #                 data["minR"], data['maxR'], data['xCenter'], data['yCenter'], data["odo"],
        #                 data["gyro"][0][0], data["gyro"][0][1], data["gyro"][0][2],
        #                 data["gyro"][1][0], data["gyro"][1][1], data["gyro"][1][2],
        #                 data["gyro"][2][0], data["gyro"][2][1], data["gyro"][2][2],
        #                 data["gyro"][3][0], data["gyro"][3][1], data["gyro"][3][2], data["bat"]]
        #     writer.writerow(FirstRow)
        #     writer.writerows(data["Lidar"][1:])
        #
        # with zipfile.ZipFile(path, 'w') as zf:
        #     for file in LidarData:
        #         filename = file + '.csv'
        #         zipdata = zipfile.ZipInfo(filename)
        #         zipdata.compress_type = zipfile.ZIP_BZIP2
        #         zipdata.date_time = time.localtime(time.time())[:6]
        #         zf.writestr(zipdata, LidarData[file].getvalue())

    def save_images(self, path='ImageData.zip'):
        self.insert_debug_msg("save_images")
        self.c.execute('''SELECT id FROM LidarData''')
        rows = self.c.fetchall()
        k = max(rows)

        ImageData = {}
        for i in range(k[0]):
            data = self.get_lidar_data_byID(i + 1)
            dt = datetime.fromtimestamp(data['Time'])
            date_time = dt.strftime("%m-%d-%Y_%H.%M.%S")

            ImageData[date_time] = data["image"]

            with zipfile.ZipFile(path, 'w') as zf:
                for file in ImageData:
                    if ImageData[file] is not None and ImageData[file] != 'Image':
                        filename = file + '.JPEG'
                        zipdata = zipfile.ZipInfo(filename)
                        zipdata.compress_type = zipfile.ZIP_BZIP2
                        zipdata.date_time = time.localtime(time.time())[:6]
                        zf.writestr(zipdata, ImageData[file])


    def drop_data(self):
        self.c.execute('''DROP TABLE IF EXISTS LidarData''')
        print('Data Deleted')

    def __exit__(self, ext_type, exc_value, traceback):
        # Closes database connections, need to read through what the functions are explicitly doing
        self.c.close()
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

def DebugPrintStore(msg,bStore):
    print(msg)
    if(bStore):
        with TurtleLidarDB() as DB:
            DB.insert_debug_msg(msg)

def DebugPrint(msg):
    DebugPrintStore(msg, True)

def printLidarStatus(msg=None, battery_voltage = -1):
    if msg is not None:
        print("STATUS: " + msg)
    with TurtleLidarDB() as DB:
        DB.update_lidar_status(msg, battery_voltage)

if __name__ == "__main__":



    with TurtleLidarDB() as db:
        #segment is to insert polarplots if missing...
        rows = db.get_all_lidar_ids()
        k = max(rows)+1
        for snap in range(1, k[0]):
            print("plot for " + str(snap))
            newplot = LidarPlot.GenerateDataPolarPlotByID(snap)
            if(not db.get_polarplot_by_lidarID(snap)):
                print(newplot)
                db.insert_polarplot(newplot, snap)
        #db.create_csv_zip()

    #with TurtleLidarDB() as db:
    #    db.create_debug_table()
        # db.insert_debug_msg("i can has debug?")
    #for i in range(0,25):
    #	DebugPrint("tendies " + str(i))
    # DebugPrint("Hello " + str(time.time()))
    # with TurtleLidarDB() as db:
    #     data = db.get_new_debug_msg_from_ID(-1)
    #     # data = db.get_last_n_debug_msg(1000)
    #     # print(data)
    #     # print("--------------------")
    #     # # #data = db.get_all_debug_msg()
    #     # # for row in data:
    #     # #     print(row[2])
    #     # lastID = data[1][0]
    #     # # print(lastID)
    #     # data = db.get_new_debug_msg_from_ID(lastID)
    #     print("Debug Table:")
    #     for row in data:
    #         print(str(row[0]) + "\t" + row[2])
    #printLidarStatus("Ready")

    # with TurtleLidarDB() as db:
    #     db.check_lidar_status_table_exists()
    #     # db.create_LidarStatus_table()
    #     X = db.get_lidar_status()
    #     print(X)
    #     db.update_lidar_status("Test...")
    #     X = db.get_lidar_status()
    #     print(X)
    #     # db.create_csv_zip()
    #     # db.save_images()
    #     # X = db.get_table_data()
    #     # print(X)

    with TurtleLidarDB() as db:
        data = db.get_lidar_data_byID(1)
        print(data)