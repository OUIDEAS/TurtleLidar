import sqlite3
from sqlite3 import Error
import csv
import pickle
import bz2


class TurtleLidarDB:
    def __enter__(self, db_file=r"C:\sqlite\db\TurtleLidarData.db"):
    # def __enter__(self, db_file="LidarData.db"):
    # def __enter__(self, db_file=r"C:\sqlite\db\LidarData.db"):
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
                "image": pickle.loads(row[11])
            }

            print(LidarData)
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

    def create_csv(self, filename='data.csv'):
        # https://stackoverflow.com/questions/10522830/how-to-export-sqlite-to-csv-in-python-without-being-formatted-as-a-list
        data = self.c.execute('''SELECT * FROM LidarData WHERE Deleted = False''')

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            # writer.writerow(['row id', 'timestamp', 'odometer', 'radius', 'angle'])
            writer.writerows(data)

    def __exit__(self, ext_type, exc_value, traceback):
        # Closes database connections, need to read through what the functions are explicitly doing
        self.c.close()
        if isinstance(exc_value, Exception):
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()


if __name__ == "__main__":
    import cv2
    import numpy as np

    with TurtleLidarDB() as db:
        # db.create_lidar_table()
        # db.delete_lidar_data(2)
        X = db.get_lidar_data(9)

    strimg = np.frombuffer(X["image"], np.uint8)
    img = cv2.imdecode(strimg, cv2.IMREAD_COLOR)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    # cv2.imwrite('Pic.png', img)
