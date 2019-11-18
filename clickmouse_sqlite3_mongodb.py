#!/usr/bin/env python3
'''
Code to count mouse clicks from buttons: Left, Middle and Right
Each click is compounding of two movements: Press and Release, then
two register are computed, also work as a Keylogger

mouse clicks are saved at SQLite3
keys pressed are saved at MongoDB

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

# -*- coding: utf-8 -*-
# Code styled according to pycodestyle
# Code parsed, checked possible errors according to pyflakes and pylint


import sys
from datetime import datetime

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
    import sqlite3

except ImportError:
    sys.exit("""You need sqlite3
        install it from http://pypi.python.org/
        or run pip3 install sqlite3""")

try:
    import pymongo

except ImportError:
    sys.exit("""You need pymongo
        install it from http://pypi.python.org/
        or run pip3 install pymongo""")

from security_conections_data import sqlite3_host1
from security_conections_data import mongodb_host1


def create_db_clickmouse():
    '''
    O SQLite é um database de apenas um arquivo.
    Informando os dados de conexão e ao criar uma tabela,
    o Database é criado. Novas tabelas podem também serem
    criadas com os dados de conexão
    '''
    try:
        conn = sqlite3.connect(sqlite3_host1)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            create table IF NOT EXISTS clickmouse (
                dt_string TEXT NOT NULL PRIMARY KEY,
                nrs_clickmouse_left INTEGER,
                nrs_clickmouse_middle INTEGER,
                nrs_clickmouse_right INTEGER
            );
            """)

        except Exception as err:
            print("ErrCurCreateTable-1 : {0}".format(err))

    except Exception as err:
        print("ErrCurCreateTable-2 : {0}".format(err))

    finally:
        if conn:
            conn.close()


def insert_first_clickmouse():
    '''
    INSERT THE FIRST ONE
    '''
    try:
        conn = sqlite3.connect(sqlite3_host1)
        cursor = conn.cursor()

        try:
            now = datetime.now()
            v_dt_string = now.strftime("%Y/%m/%d")

            cursor.execute("""
            INSERT INTO clickmouse (dt_string,
                                    nrs_clickmouse_left,
                                    nrs_clickmouse_middle,
                                    nrs_clickmouse_right)
            VALUES (?, ?, ?, ?)
            """, (v_dt_string, 0, 0, 0))

            conn.commit()

        except Exception:
            pass
            # print("ErrInsert-1 : {0}".format(err))

    except Exception as err:
        print("ErrInsert-2 : {0}".format(err))

    finally:
        if conn:
            conn.close()


def show_all_records():
    '''
    Show all records inserted
    '''
    try:
        conn = sqlite3.connect(sqlite3_host1)
        cursor = conn.cursor()

        try:
            cursor.execute("""
            SELECT *
            FROM clickmouse
            """)

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

            #if v_i > 0:
            print('+---------------------------------------------+')
            print(
                "|",
                ' AVERAGE  ',
                '{:>10}'.format(round(v_nrs_clickmouse_left / v_i, 4)),
                '{:>10}'.format(round(v_nrs_clickmouse_middle / v_i, 4)),
                '{:>10}'.format(round(v_nrs_clickmouse_right / v_i, 4)),
                "|")

            print('+---------------------------------------------+')

        except Exception as err:
            print("ErrSelectAll-1 : {0}".format(err))

    except Exception as err:
        print("ErrSelectAll-2 : {0}".format(err))

    finally:
        if conn:
            conn.close()


def clicked(x, y, button, pressed):
    '''
    Control clicks
    '''
    if button == mouse.Button.left:
        # Left Button was clicked
        try:
            conn = sqlite3.connect(sqlite3_host1)
            cursor = conn.cursor()

            try:
                now = datetime.now()
                v_dt_string = now.strftime("%Y/%m/%d")

                cursor.execute("""
                SELECT nrs_clickmouse_left
                FROM clickmouse
                where dt_string = ?
                """, (v_dt_string,))

                v_qtde = 0
                records = cursor.fetchone()

                if records:
                    for i in records:
                        v_qtde = i

                    if conn:
                        conn.close()
                else:
                    if conn:
                        conn.close()
                    create_db_clickmouse()
                    insert_first_clickmouse()

            except Exception as err:
                print("ErrSelect_Left-1 : {0}".format(err))

            try:
                conn = sqlite3.connect(sqlite3_host1)
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE clickmouse
                SET nrs_clickmouse_left = ?
                where dt_string = ?
                """, (v_qtde + 1, v_dt_string))

                conn.commit()

            except Exception as err:
                print("ErrUpdate_Left-2 : {0}".format(err))

        except Exception as err:
            print("ErrUpdate_Left-3 : {0}".format(err))

        finally:
            if conn:
                conn.close()

    if button == mouse.Button.middle:
        # Middle Button was clicked
        try:
            conn = sqlite3.connect(sqlite3_host1)
            cursor = conn.cursor()

            try:
                now = datetime.now()
                v_dt_string = now.strftime("%Y/%m/%d")

                cursor.execute("""
                SELECT nrs_clickmouse_middle
                FROM clickmouse
                where dt_string = ?
                """, (v_dt_string,))

                v_qtde = 0
                records = cursor.fetchone()

                if records:
                    for i in records:
                        v_qtde = i

                    if conn:
                        conn.close()
                else:
                    if conn:
                        conn.close()
                    create_db_clickmouse()
                    insert_first_clickmouse()

            except Exception as err:
                print("ErrSelect_Middle-1 : {0}".format(err))

            try:
                conn = sqlite3.connect(sqlite3_host1)
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE clickmouse
                SET nrs_clickmouse_middle = ?
                where dt_string = ?
                """, (v_qtde + 1, v_dt_string))

                conn.commit()

            except Exception as err:
                print("ErrUpdate_Middle-2 : {0}".format(err))

        except Exception as err:
            print("ErrUpdate_Middle-3 : {0}".format(err))

        finally:
            if conn:
                conn.close()

    if button == mouse.Button.right:
        # Right Button was clicked
        try:
            conn = sqlite3.connect(sqlite3_host1)
            cursor = conn.cursor()

            try:
                now = datetime.now()
                v_dt_string = now.strftime("%Y/%m/%d")

                cursor.execute("""
                SELECT nrs_clickmouse_right
                FROM clickmouse
                where dt_string = ?
                """, (v_dt_string,))

                v_qtde = 0
                records = cursor.fetchone()

                if records:
                    for i in records:
                        v_qtde = i

                    if conn:
                        conn.close()
                else:
                    if conn:
                        conn.close()
                    create_db_clickmouse()
                    insert_first_clickmouse()

            except Exception as err:
                print("ErrSelect_Right-1 : {0}".format(err))

            try:
                conn = sqlite3.connect(sqlite3_host1)
                cursor = conn.cursor()

                cursor.execute("""
                UPDATE clickmouse
                SET nrs_clickmouse_right = ?
                where dt_string = ?
                """, (v_qtde + 1, v_dt_string))

                conn.commit()

            except Exception as err:
                print("ErrUpdate_Right-2 : {0}".format(err))

        except Exception as err:
            print("ErrUpdate_Right-3 : {0}".format(err))

        finally:
            if conn:
                conn.close()


def on_press(key):
    '''
    INSERT DOCUMENT INTO MONGODB
    '''
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
                raise Exception("Error during insert of MongoDB Document on_press def")

        except Exception as err:
            print("ErrOn_Press-1 : {0}".format(err))

        finally:
            if conn2:
                conn2.close()

    except AttributeError:
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
                raise Exception("Error during insert of MongoDB Document Special Key Pressed")

        except Exception as err:
            print("ErrOn_Press-2 : {0}".format(err))

    finally:
        if conn2:
            conn2.close()


def on_release(key):
    '''
    release when ESC key pressed
    '''
    if key == keyboard.Key.esc:
        # Stop listener
        return False


def listening():
    '''
    LISTENER
    '''
    try:
        with MouseListener(on_click=clicked) as listener:
            with keyboard.Listener(on_press=on_press,
                                   on_release=on_release) as listener:
                listener.join()

    except Exception as err:
        print("ErrListening-1 : {0}".format(err))


if __name__ == '__main__':
    create_db_clickmouse()
    insert_first_clickmouse()
    show_all_records()
    listening()
    show_all_records()
