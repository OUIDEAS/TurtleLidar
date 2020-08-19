import sqlite3
from sqlite3 import Error
import time
from datetime import datetime
import csv
import pickle
import bz2
import io
import zipfile

class TurtleLidarDB:
    def __enter__(self, db_file="LidarData.db"):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            self.c = self.conn.cursor()
        except Error as e:
            print(e)

        return self

    def create_lidar_table(self):
        create_table_sql = """CREATE TABLE IF NOT EXISTS LidarData (
                                            id integer PRIMARY KEY,
                                            timestamp REAL NOT NULL,
                                            odometer REAL,
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
        except Error as e:
            print(e)

    def create_lidar_data_input(self, Time, odo, lidar, avgR, stdR, minR, maxR, xCenter, yCenter, gyro, image, batVolt):
        # lidar = tuple(zip(angle, radius))
        Lidar = pickle.dumps(lidar)
        LIDAR = bz2.compress(Lidar)
        Gyro = pickle.dumps(gyro)
        # GYRO = bz2.compress(Gyro)
        Image = pickle.dumps(image)
        # IMAGE = bz2.compress(Image)

        sql = ''' INSERT INTO LidarData (timestamp,odometer,lidar,avgR,stdR,minR,maxR,xCenter,yCenter,gyro,Image, batVolt, Deleted)
                      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''

        # cur = conn.cursor()
        # for item in range(len(radius)):
        de = "False"
        data = (Time, odo, LIDAR, avgR, stdR, minR, maxR, xCenter, yCenter, Gyro, Image, batVolt, de)
        self.c.execute(sql, data)

        return self.c.lastrowid

    def get_table_data(self):
        self.c.execute('''SELECT id,timestamp,odometer, avgR, stdR, minR, maxR, xCenter, yCenter, batVolt FROM LidarData''')
        rows = self.c.fetchall()
        # Y = []
        # for row in rows:
        #     print(row)
        #     X = [0 if v is None else v for v in row]
        #     Y.append(X)
        return rows

    def get_lidar_data(self, rowID=1):
        self.c.execute("SELECT * FROM LidarData WHERE id=?", (rowID,))

        rows = self.c.fetchall()
        if len(rows) == 0:
            LidarData = None
        for row in rows:

            LidarData = {
                "Lidar": pickle.loads(bz2.decompress(row[3])),
                "Time": row[1],
                "odo": row[2],
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

    def create_csv(self):
        self.c.execute('''SELECT id FROM LidarData''')
        rows = self.c.fetchall()
        k = max(rows)

        ImageData = {}
        LidarData = {}
        for i in range(k[0]):
            data = self.get_lidar_data(i+1)
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

    def save_images(self, path='ImageData.zip'):
        self.c.execute('''SELECT id FROM LidarData''')
        rows = self.c.fetchall()
        k = max(rows)

        ImageData = {}
        for i in range(k[0]):
            data = self.get_lidar_data(i + 1)
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

    def create_csv_zip(self, path='LidarData.zip'):
        self.c.execute('''SELECT id FROM LidarData''')
        rows = self.c.fetchall()
        k = max(rows)

        LidarData = {}
        for i in range(k[0]):
            data = self.get_lidar_data(i + 1)
            dt = datetime.fromtimestamp(data['Time'])
            date_time = dt.strftime("%m-%d-%Y_%H.%M.%S")
            LidarData[date_time] = io.StringIO()

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

        with zipfile.ZipFile(path, 'w') as zf:
            for file in LidarData:
                filename = file + '.csv'
                zipdata = zipfile.ZipInfo(filename)
                zipdata.compress_type = zipfile.ZIP_BZIP2
                zipdata.date_time = time.localtime(time.time())[:6]
                zf.writestr(zipdata, LidarData[file].getvalue())

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


if __name__ == "__main__":

    with TurtleLidarDB() as db:
        db.create_csv_zip()
        # db.save_images()
