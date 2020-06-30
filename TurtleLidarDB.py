import sqlite3
from sqlite3 import Error
import csv
import pickle


class TurtleLidarDB:
    def __enter__(self, db_file=r"C:\sqlite\db\TurtleLidarData.db"):

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
                                            stdR REAL
                                        );"""

        try:
            self.c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_lidar_data_input(self, Time, odo, lidar, avgR, stdR):
        # lidar = tuple(zip(angle, radius))
        Lidar = pickle.dumps(lidar)

        sql = ''' INSERT INTO LidarData (timestamp,odometer,lidar,avgR,stdR)
                      VALUES(?,?,?,?,?) '''

        # cur = conn.cursor()
        # for item in range(len(radius)):
        data = (Time, odo, Lidar, avgR, stdR)
        self.c.execute(sql, data)

        return self.c.lastrowid

    def get_lidar_data(self, rowID=1):
        self.c.execute("SELECT * FROM LidarData WHERE id=?", (rowID,))

        rows = self.c.fetchall()
        for row in rows:

            LidarData = {
                "Lidar": pickle.loads(row[3]),
                "Time": row[1],
                "odo": row[2],
                "AvgR": row[4],
                "StdRadius": row[5]
            }
            print(LidarData)
        return LidarData

    def create_csv(self, filename='data.csv'):
        # https://stackoverflow.com/questions/10522830/how-to-export-sqlite-to-csv-in-python-without-being-formatted-as-a-list
        data = self.c.execute("SELECT * FROM LidarData")

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

    with TurtleLidarDB() as db:
        db.get_lidar_data()
        # db.create_lidar_table()