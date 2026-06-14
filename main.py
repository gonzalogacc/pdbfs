#!/usr/bin/env python
import io
import json
import os, stat, errno

# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import db
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)

hello_path = '/hello'
hello_str = b'Hello World!\n'

tables = db.list_tables()
        
class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0


logfile = open("/tmp/logs.log", 'w') 

def log(message: str):
    logfile.write(f"{message}\n")
    logfile.flush()

class DBFS(Fuse):

    def getattr(self, path):
        st = MyStat()
        # Clean path and split
        pelements = [p for p in path.split('/') if p]
        
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
            return st

        if len(pelements) == 1 and pelements[0] in tables:
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st
            
        if len(pelements) == 2 and pelements[0] in tables and pelements[1].endswith(".column"):
            st.st_mode = stat.S_IFDIR | 0o555
            st.st_nlink = 2
            return st

        if len(pelements) == 3 and pelements[0] in tables and pelements[1].endswith(".column") and pelements[2].endswith('.dbf'):
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            st.st_size = 4096 # Placeholder, ideally dynamic but 4k is safer than 999999
            return st

        return -errno.ENOENT

    def readdir(self, path, offset):
        pelements = [p for p in path.split('/') if p]
        dirs = ['.', '..']
        
        if path == '/':
            dirs.extend(tables)

        elif len(pelements) == 1 and pelements[0] in tables:
            table_name = pelements[0].replace(".table", "")
            dirs.extend(db.list_table_columns(table_name))

        elif len(pelements) == 2 and pelements[0] in tables and pelements[1].endswith('.column'):
            table_name = pelements[0].replace('.table', '')
            column_name = pelements[1].replace('.column', '')
            dirs.extend(db.list_column_rows(table_name, column_name))

        for r in dirs:
            yield fuse.Direntry(r)

    def open(self, path, flags):
        pelements = [p for p in path.split('/') if p]
        if len(pelements) != 3 or not pelements[2].endswith('.dbf'):
            return -errno.ENOENT
        
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        pelements = [p for p in path.split('/') if p]
        if len(pelements) != 3 or not pelements[2].endswith(".dbf"):
            return -errno.ENOENT
        
        tablename = pelements[0].replace('.table', '')
        column_name = pelements[1].replace('.column', '')
        column_value = pelements[2].replace('.dbf', '')
        
        response = db.read_table_data(tablename, column_name, column_value)
        lines = [", ".join(str(item) for item in row) for row in response]
        file_content = "\n".join(lines) + "\n"
        
        payload = file_content.encode('utf-8')
        
        slen = len(payload)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            buf = payload[offset:offset+size]
        else:
            buf = b''
        return buf

def main():
    usage="""
Userspace postgres mount

""" + Fuse.fusage
    server = DBFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()