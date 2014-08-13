from __future__ import print_function
import sqlite3
import time
import os
import subprocess
import shutil
import sys
from meta import Meta
import traceback


class DataBaseManager(sqlite3.Cursor):
    """docstring for DataBaseManager"""
    def __init__(self, dbPath):

        self.conn = sqlite3.connect(dbPath)
        # self.cursor = conn.cursor()

        super(DataBaseManager, self).__init__(self.conn)

    def canProceed(self):
        query = """SELECT origin FROM media WHERE status='converting' """
        self.execute(query)
        result = self.fetchone()
        return result is None

    def getQueuedFile(self):
        query = """SELECT * FROM media WHERE status='queued' """
        self.execute(query)
        return self.fetchall()

    def UPDATE(self, fileOrigin, field, value):
        query = """ UPDATE media SET {} = ?, lastchanged=? WHERE origin=? """.format(field)
        self.execute(query, (value, time.time(), fileOrigin))
        self.commit()

    def commit(self):
        self.conn.commit()


def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)


def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)


def convert(fileOrigin, fileDestination):
    f = open('out.log', 'w')
    f.write(fileDestination.split('/')[-1].split('.')[0])
    f.flush()

    cmd_prime = ['nice', '/usr/bin/HandBrakeCLI']
    cmd_prime.append('-i')
    cmd_prime.append(fileOrigin)
    cmd_prime.append('-o')
    cmd_prime.append(fileDestination)
    cmd_prime.append('-e')
    cmd_prime.append('x264')
    cmd_prime.append('-q')
    cmd_prime.append('20.0')
    cmd_prime.append('-r')
    cmd_prime.append('30')
    cmd_prime.append('--pfr')
    cmd_prime.append('-a')
    cmd_prime.append('1,1')
    cmd_prime.append('-E')
    cmd_prime.append('faac,copy:ac3')
    cmd_prime.append('-B')
    cmd_prime.append('160,160')
    cmd_prime.append('-6')
    cmd_prime.append('dpl2,none')
    cmd_prime.append('-R')
    cmd_prime.append('Auto,Auto')
    cmd_prime.append('-D')
    cmd_prime.append('0.0,0.0')
    cmd_prime.append('--audio-copy-mask')
    cmd_prime.append('aac,ac3,dtshd,dts,mp3')
    cmd_prime.append('--audio-fallback')
    cmd_prime.append('ffac3')
    cmd_prime.append('-f')
    cmd_prime.append('mp4')
    cmd_prime.append('-4')
    cmd_prime.append('-X')
    cmd_prime.append('1280')
    cmd_prime.append('-Y')
    cmd_prime.append('720')
    cmd_prime.append('--loose-anamorphic')
    cmd_prime.append('--modulus')
    cmd_prime.append('2')
    cmd_prime.append('-m')
    cmd_prime.append('--x264-preset')
    cmd_prime.append('medium')
    cmd_prime.append('--h264-profile')
    cmd_prime.append('high')
    cmd_prime.append('--h264-level')
    cmd_prime.append('3.1')


    # cmd = """nice /usr/bin/HandBrakeCLI -i "{}" -o  "{}" """.format(fileOrigin, fileDestination)
    # cmd += """ -e x264  -q 20.0 -r 30 --pfr  -a 1,1 -E faac,copy:ac3 -B 160,160 -6 dpl2,none -R Auto,Auto -D 0.0,0.0 --audio-copy-mask aac,ac3,dtshd,dts,mp3 --audio-fallback ffac3 -f mp4 -4 -X 1280 -Y 720 --loose-anamorphic --modulus 2 -m --x264-preset medium --h264-profile  high --h264-level 3.1"""

    # print cmd
    # print cmd_prime
    # subprocess.call(cmd, shell=True)
    p = subprocess.Popen(cmd_prime, stdout=f)
    p.communicate()


def metaData(fileOrigin, dbPath):

    dirs = fileOrigin.split('/')
    kindIndex = dirs.index('TV Show')

    metaD = {}
    # videoKind, showName, seasonNumber, episodeNumber
    videoKind = 'Movie'
    if len(dirs) - 2 > kindIndex:
        # return 'Movie', None, None, None
        videoKind = 'TV show'
    metaD['videoKind'] = videoKind


    showNameIndex = kindIndex + 1
    showName = None
    if len(dirs) - 2 >= showNameIndex:
        showName = dirs[showNameIndex]
        # return 'TV show', dirs[showNameIndex], None, None
    metaD['showName'] = showName

    seasonNumberIndex = kindIndex + 2
    seasonNumber = None
    if len(dirs) - 2 >= seasonNumberIndex:
        seasonNumber = int(dirs[seasonNumberIndex])
        # return 'TV show', dirs[showNameIndex], dirs[seasonNumberIndex], None
    metaD['seasonNumber'] = seasonNumber

    episodeNumberIndex = kindIndex + 3
    # TV Show name and season number specified
    episodeNumber = None
    if len(dirs) - 2 >= episodeNumberIndex:
        episodeNumber = int(dirs[episodeNumberIndex])
        # return 'TV show', dirs[showNameIndex], dirs[seasonNumberIndex], dirs[episodeNumberIndex]
    metaD['episodeNumber'] = episodeNumber

    if showName is not None and seasonNumber is not None and episodeNumber is not None:
        meta = Meta(dbPath)
        soup = meta.get_meta(showName, seasonNumber, episodeNumber)
        print("Episode Name and Description: {}".format(soup))
        if soup is None:
            metaD['episodeName'] = None
            metaD['episodeDescription'] = None
        else:
            episodeName, episodeDescription = soup
            metaD['episodeName'] = episodeName
            metaD['episodeDescription'] = episodeDescription
    else:
        metaD['episodeName'] = None
        metaD['episodeDescription'] = None

    return metaD


def importiTunes(fileOrigin, videoKind, showName, seasonNumber, episodeNumber, episodeName, episodeDescription):
    cmd = ["/usr/bin/osascript"]
    cmd.append("/Users/alexis/Developer/Media/import_iTunes.scpt")
    cmd.append(str(fileOrigin))
    cmd.append(str(videoKind))
    cmd.append(str(showName))
    cmd.append(str(seasonNumber))
    cmd.append(str(episodeNumber))
    cmd.append(str(episodeDescription))
     # '{0}' '{1}' '{2}' {3} {4}".format(fileOrigin, videoKind, showName, seasonNumber, episodeNumber)

    print(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    print("OUTPUT iTunes import")
    print(out)
    print("ERROR iTunes import")
    print(err)

    return out


def main():
    args = sys.argv
    basePath = args[1]
    dbPath = os.path.join(basePath, 'media.db')
    dbManager = DataBaseManager(dbPath)

    if not dbManager.canProceed():
        return
    filesToConvert = dbManager.getQueuedFile()
    if len(filesToConvert) == 0:
        return

    for fileToConvert in filesToConvert:
        try:
            fileOrigin = fileToConvert[0]
            fileDestination = fileToConvert[1]

            metaD = metaData(fileOrigin, dbPath)
            print('Meta Data from IMDB')
            print(metaD)

            dbManager.UPDATE(fileOrigin, 'status', 'converting')

            if metaD['episodeName'] is not None:
                fileName, fileExtension = os.path.splitext(fileDestination)
                baseDir = fileName.split('/')
                baseDir = os.path.join(*baseDir[:-1])
                fileDestination = os.path.join(baseDir, metaD['episodeName'] + '.m4v')

            convert(fileOrigin, fileDestination)
            dbManager.UPDATE(fileOrigin, 'status', 'done')
        except Exception:
            dbManager.UPDATE(fileOrigin, 'status', 'error')
            error(traceback.print_exc())
            # raise e

        out = importiTunes(fileDestination, **metaD)

        home = os.path.expanduser("~")
        trash = os.path.join(home, ".Trash")

        try:
            shutil.move(fileOrigin, trash)
            shutil.move(fileDestination, trash)
        except shutil.Error:
            # Eventually send a notification
            pass

        dbManager.UPDATE(fileOrigin, 'imported', 1)


if __name__ == '__main__':
    main()
