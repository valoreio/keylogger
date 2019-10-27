#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Code styled according to pycodestyle


__author__ = "Marcos Aurelio Barranco"
__copyright__ = "Copyright 2016, The MIT License (MIT)"
__credits__ = ["Marcos Aurelio Barranco", ]
__license__ = "MIT"
__version__ = "2"
__maintainer__ = "Marcos Aurelio Barranco"
__email__ = ""
__status__ = "Production"


'''
mouse clicks are saved at PostgreSQL
keys pressed are saved at MongoDB

Code to count mouse clicks from buttons: Left, Middle and Right
Each click is compounding of two movements: Press and Release, then
two register are computed, also work as a Keylogger

Relational concept <----------> MongoDB equivalent
      Database                       Database
      Tables                         Collections
      Rows                           JSON Documents compiled to BSON
      Column                         Field or Key
      Value                          Value
      Record                         Document
      Index                          Index
      Primary Key                    _id
      Join                           Embedding, Linking, $lookup
      Partition                      Shard
      Usa FK                         Não usa FK
      Usa Triggers                   Não usa Triggers
      Escalável verticalmente        Escalável horizontalmente
          mais memória                  mais servidores
      ACID(Atomicity,Consistency,    CAP(Consistency,
           Isolation,Durability)         Availability,
                                         Partition-Tolerance)
                                     ACID in version 4.0
'''

from datetime import datetime
from security_conections_data import admpostgresql_host1
from security_conections_data import admubuntuiot_host1
from security_conections_data import mongodb_host1

try:
    import pynput

except ImportError:
    sys.exit("""You need pynput
        install it from http://pypi.python.org/
        or run pip3 install pynput""")

from pynput import keyboard
from pynput import mouse
from pynput.mouse import Listener as MouseListener
from pynput.mouse import Button

try:
    import psycopg2

except ImportError:
    sys.exit("""You need psycopg2
        install it from http://pypi.python.org/
        or run pip3 install psycopg2""")

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    import pymongo

except ImportError:
    sys.exit("""You need pymongo
        install it from http://pypi.python.org/
        or run pip3 install pymongo""")


def create_db_ubuntuiot():
    # CREATE DB IF NOT EXISTS ubuntuiot - PostgreSQL
    '''
    OS files do PostgreSQL encontram-se em:
    DataDirectory: /var/lib/postgresql/<version>/main
    LogFile      : /var/log/postgresql/postgresql-10-main.log
    =# 'contra barra' conninfo

    =# SHOW DATA_DIRECTORY;
     data_directory
    -----------------------
    /var/lib/postgresql/9.5/main

    =# SELECT pg_relation_filepath('pg_database');
     pg_relation_filepath
    ---------------------
    global/1262

    =# SELECT pg_relation_filepath('clickmouse');
     pg_relation_filepath
    ----------------------
    base/16385/16386
    '''
    try:
        conn = psycopg2.connect(**admpostgresql_host1)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        try:
            cursor.execute("""SELECT datname 
                FROM pg_catalog.pg_database 
                WHERE datname = 'ubuntuiot'""")

            records = cursor.fetchall()

            if not records: # DB unavailable
                try:
                    cursor.execute("""CREATE DATABASE ubuntuiot
                        WITH OWNER = admpostgres
                        ENCODING = 'UTF8'
                        TEMPLATE = template0
                        TABLESPACE = pg_default
                        LC_COLLATE = 'en_US.UTF-8'
                        LC_CTYPE = 'C.UTF-8'
                        CONNECTION LIMIT = -1;""")

                except Exception as e:
                    raise Exception("ErrCurCreateDB-1 : {0}".format(e))

                try:
                    cursor.execute("""GRANT CONNECT,
                        TEMPORARY ON DATABASE ubuntuiot TO public;""")

                except Exception as e:
                    raise Exception("ErrGrantConnDB-2 : {0}".format(e))

                try:
                    cursor.execute("""GRANT ALL ON DATABASE ubuntuiot
                        TO postgres;""")

                except Exception as e:
                    raise Exception("ErrGrantAllDB-3 : {0}".format(e))

                try:
                    cursor.execute("""GRANT ALL ON DATABASE ubuntuiot
                        TO admpostgres;""")

                except Exception as e:
                    raise Exception("ErrGrantAllDB-4 : {0}".format(e))

        except Exception as e:
            raise Exception("ErrCurCreateDB-5 : {0}".format(e))

    except Exception as e:
        raise Exception("ErrCurCreateDB-6 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()


def create_table_clickmouse():
    # CREATE TABLE IF NOT EXISTS clickmouse - PostgreSQL
    try:
        conn = psycopg2.connect(**admubuntuiot_host1)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        try:
            cursor.execute("""create table IF NOT EXISTS clickmouse (
                dt_string TEXT NOT NULL PRIMARY KEY,
                nrs_clickmouse_left INTEGER,
                nrs_clickmouse_middle INTEGER,
                nrs_clickmouse_right INTEGER);""")

        except Exception as e:
            raise Exception("ErrCurCreateTable-1 : {0}".format(e))

    except Exception as e:
        raise Exception("ErrCurCreateTable-2 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()


def insert_first_clickmouse():
    # INSERT THE FIRST ONE
    try:
        conn = psycopg2.connect(**admubuntuiot_host1)
        cursor = conn.cursor()

        try:
            now = datetime.now()
            v_dt_string = now.strftime("%Y/%m/%d")

            postgres_insert = """INSERT INTO clickmouse (dt_string,
                nrs_clickmouse_left,
                nrs_clickmouse_middle,
                nrs_clickmouse_right)
                VALUES (%s, %s, %s, %s)"""

            record_to_insert = (v_dt_string, 0, 0, 0)

            cursor.execute(postgres_insert, record_to_insert)

            conn.commit()

        except Exception as e:
            pass
            #raise Exception("ErrInsert-1 : {0}".format(e))

    except Exception as e:
        raise Exception("ErrInsert-2 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()


def show_all_records():
    # Show all records inserted
    try:
        conn = psycopg2.connect(**admubuntuiot_host1)
        cursor = conn.cursor()

        try:
            cursor.execute("""SELECT *
                FROM clickmouse
                ORDER BY dt_string DESC""")

            records = cursor.fetchall()

            print('+---------------------------------------------+')
            print("|         Hit 'Esc' to finish the code!       |")
            print('+---------------------------------------------+')
            print('|           ------------B U T T O N S-------- |')
            print('|  DATE(PK)        LEFT     MIDDLE      RIGHT |')
            print('+---------------------------------------------+')
            v_i = 0
            v_nrs_clickmouse_left = 0
            v_nrs_clickmouse_middle = 0
            v_nrs_clickmouse_right = 0

            for i in records:
                v_i += 1
                v_nrs_clickmouse_left += i[1]
                v_nrs_clickmouse_middle += i[2]
                v_nrs_clickmouse_right += i[3]
                print(
                    "|",
                    '{:10}'.format(i[0]),
                    '{:>10}'.format(i[1]),
                    '{:>10}'.format(i[2]),
                    '{:>10}'.format(i[3]),
                    "|")

            if v_i > 0:
                print('+---------------------------------------------+')
                print(
                    "|",
                    ' AVERAGE  ',
                    '{:>10}'.format(round(v_nrs_clickmouse_left / v_i, 4)),
                    '{:>10}'.format(round(v_nrs_clickmouse_middle / v_i, 4)),
                    '{:>10}'.format(round(v_nrs_clickmouse_right / v_i, 4)),
                    "|")

            print('+---------------------------------------------+')

        except Exception as e:
            raise Exception("ErrSelectAll-1 : {0}".format(e))

    except Exception as e:
        raise Exception("ErrSelectAll-2 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()


def increment_click(incr_select, incr_update):
    # SELECT
    try:
        conn = psycopg2.connect(**admubuntuiot_host1)
        cursor = conn.cursor()
        now = datetime.now()
        v_dt_string = now.strftime("%Y/%m/%d")
        cursor.execute(incr_select, (v_dt_string,))
        v_qtde = 0
        records = cursor.fetchone()

        if records:
            for i in records:
                v_qtde = i

        else:
            if conn:
                cursor.close()
                conn.close()

            create_db_ubuntuiot()
            create_table_clickmouse()
            insert_first_clickmouse()

    except Exception as e:
        raise Exception("ErrSelect-1 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()

    # UPDATE
    try:
        conn = psycopg2.connect(**admubuntuiot_host1)
        cursor = conn.cursor()
        cursor.execute(incr_update, (v_qtde + 1, v_dt_string,))
        conn.commit()

    except Exception as e:
        raise Exception("ErrUpdate-1 : {0}".format(e))

    finally:
        if conn:
            cursor.close()
            conn.close()


def clicked(x, y, button, pressed):
    # Handle clicks
    if button == mouse.Button.left:
        # Left Button was clicked

        incr_select = """SELECT nrs_clickmouse_left
            FROM clickmouse
            where dt_string = %s"""

        incr_update = """UPDATE clickmouse
            SET nrs_clickmouse_left = %s
            where dt_string = %s"""

        
    if button == mouse.Button.middle:
        # Middle Button was clicked

        incr_select = """SELECT nrs_clickmouse_middle
            FROM clickmouse
            where dt_string = %s"""

        incr_update = """UPDATE clickmouse
            SET nrs_clickmouse_middle = %s
            where dt_string = %s"""


    if button == mouse.Button.right:
        # Right Button was clicked

        incr_select = """SELECT nrs_clickmouse_right
            FROM clickmouse
            where dt_string = %s"""

        incr_update = """UPDATE clickmouse
            SET nrs_clickmouse_right = %s
            where dt_string = %s"""

    increment_click(incr_select, incr_update)


def on_press(key):
    # INSERT DOCUMENT INTO MONGODB
    try:
        # Testa o atributo do caracter,
        # se der erro já pula tudo sem perder tempo
        _ = key.char

        # char key pressed
        try:
            conn2 = pymongo.MongoClient(**mongodb_host1)
            # keylogger é o Database
            db = conn2.keylogger

            now = datetime.now()
            v_dt_string = now.strftime("%Y/%m/%d-%H:%M:%S:%f")

            post = {"date": v_dt_string,
                    "keypressed": key.char
                    }

            # keylogger_co é a Collection
            # post é o Document
            result = db.keylogger_co.insert_one(post)
            if not result.acknowledged:
                raise Exception(
                    "Error during insert of MongoDB Document on_press def")

        except Exception as e:
            raise Exception("ErrOn_Press-1 : {0}".format(e))

        finally:
            if conn2:
                conn2.close()

    except AttributeError as e:
        # special key pressed
        try:
            conn2 = pymongo.MongoClient(**mongodb_host1)
            # keylogger é o Database
            db = conn2.keylogger

            now = datetime.now()
            v_dt_string = now.strftime("%Y/%m/%d-%H:%M:%S:%f")

            post = {
                "date": v_dt_string,
                "keypressed": str(key)
            }

            # keylogger_co é a CollectionMongod
            # post é o Document
            result = db.keylogger_co.insert_one(post)
            if not result.acknowledged:
                raise Exception(
                    "MongoDB: Error during insert-Special Key Pressed")

        except Exception as e:
            raise Exception("ErrOn_Press-2 : {0}".format(e))

    finally:
        if conn2:
            conn2.close()


def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


def listening():
    try:
        with MouseListener(on_click=clicked) as listener:
            with keyboard.Listener(on_press=on_press,
                                   on_release=on_release) as listener:
                listener.join()

    except Exception as e:
        raise Exception("ErrListening-1 : {0}".format(e))


def main():
    create_db_ubuntuiot()
    create_table_clickmouse()
    insert_first_clickmouse()
    show_all_records()
    listening()
    show_all_records()


if __name__ == '__main__':
    main()
