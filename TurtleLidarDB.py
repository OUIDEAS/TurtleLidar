import sqlite3
from sqlite3 import Error
import csv


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
                                            timestamp text NOT NULL,
                                            odometer text,
                                            radius text,
                                            angle text
                                        );"""

        try:
            self.c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_lidar_data_input(self, dataInput):
        dateTime = dataInput[0]
        odom = dataInput[1]
        radius = dataInput[2]
        angle = dataInput[3]

        sql = ''' INSERT INTO LidarData (timestamp,odometer,radius,angle)
                      VALUES(?,?,?,?) '''

        # cur = conn.cursor()
        for item in range(len(radius)):
            data = (dateTime, odom, radius[item], angle[item])
            self.c.execute(sql, data)
        return self.c.lastrowid

    def get_lidar_data(self):
        self.c.execute("SELECT * FROM LidarData")

        rows = self.c.fetchall()
        for row in rows:
            print(row)
        return rows

    def create_csv(self, filename='data.csv'):
        # https://stackoverflow.com/questions/10522830/how-to-export-sqlite-to-csv-in-python-without-being-formatted-as-a-list
        data = self.c.execute("SELECT * FROM LidarData")

        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['row id', 'timestamp', 'odometer', 'radius', 'angle'])
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
        # db.create_csv()
        db.get_lidar_data()
        # db.create_lidar_table()