import sqlite3
import time
import os
from convert import DataBaseManager
import sys


def fileAllowed(fileOrigin):
    fileName, fileExtension = os.path.splitext(fileOrigin)
    accepted_extensions = [".avi", ".mkv", ".mp4"]

    return fileExtension in accepted_extensions

def destination(fileOrigin):
    fileName, fileExtension = os.path.splitext(fileOrigin)
    return fileName + ".m4v"


def getMovies(basePath):
    movie_list = []

    for root, sub, files in os.walk(basePath):
        for f in files:
            if fileAllowed(f):
                movie_list.append(os.path.join(root, f))

    return movie_list


def main():
    args = sys.argv
    basePath = args[1]
    dbPath = os.path.join(basePath, 'media.db')

    dbManager = DataBaseManager(dbPath)
    for movie in getMovies(basePath):
        
        dbManager.execute("""SELECT * FROM media WHERE origin=? """, (movie,))
        result = dbManager.fetchone()
        if result is None:

            dbManager.execute("""INSERT INTO media VALUES (?, ?, 'queued', 0, ?) """, (movie, destination(movie), time.time()))
            dbManager.commit()

if __name__ == '__main__':
    main()