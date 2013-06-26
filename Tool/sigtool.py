# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import sys
import os
import hashlib
import marshal
import shutil
import zlib
import time
import struct
from optparse import OptionParser

SIGDB_FILENAME = 'sigtool.mdb'

#---------------------------------------------------------------------
# PrintLogo()
# Ű�޹���� �ΰ� ����Ѵ�
#---------------------------------------------------------------------
def PrintLogo() :
    logo = 'KICOM Anti-Virus II (for %s) Ver %s (%s)\nCopyright (C) 1995-%s Kei Choi. All rights reserved.\n'

    print '------------------------------------------------------------'
    print 'KICOM Anti-Virus II : Signature Tool (sigtool) ver 0.1      '
    print 'Copyright (C) 1995-2013 Kei Choi. All rights reserved.        '
    print '------------------------------------------------------------'

#---------------------------------------------------------------------
# PrintUsage()
# sigtool�� ������ �����ش�.
#---------------------------------------------------------------------
def PrintUsage() :
    print '\nUsage: sigtool.py [options]'

#---------------------------------------------------------------------
# PrintOptions()
# sigtool�� �ɼ��� ����Ѵ�
#---------------------------------------------------------------------
def PrintOptions() :
    options_string = \
'''Options:
        --md5 [FILE]                generate MD5 sigs for FILES
        --pack [DB FILE Prefix]     pack a MDB file (default ID : 1)
        --id [NUM]                  pattern ID (with --pack option)
        -?,  --help                 this help'''

    print options_string

#---------------------------------------------------------------------
# DefineOptions()
# sigtool�� �ɼ��� �����Ѵ�
#---------------------------------------------------------------------
def DefineOptions() :
    try :
        usage = "Usage: %prog [options]"
        parser = OptionParser(add_help_option=False, usage=usage)

        parser.add_option("", "--md5",
                      action="store", type="string", dest="md5_fname")
        parser.add_option("", "--pack",
                      action="store", type="string", dest="pack_fname")
        parser.add_option("", "--id",
                      action="store", type="int", dest="id_num", default = 1)

        return parser
    except :
        pass

    return None

#---------------------------------------------------------------------
# ParserOptions()
# sigtool�� �ɼ��� �м��Ѵ�
#---------------------------------------------------------------------
def ParserOptions() :
    parser = DefineOptions()

    if parser == None or len( sys.argv ) < 2 :
        return None, None
    else :
        try :
            (options, args) = parser.parse_args()
        except :
            return None, None

        return options, args

def Func_MD5(filename) :
    try :
        fp = open(filename, 'rb')
        data = fp.read()
        fp.close()

        md5 = hashlib.md5()
        md5.update(data)
        f_md5 = md5.hexdigest()

        fp = open(SIGDB_FILENAME, 'a+t')
        fname = os.path.basename(filename) # ���� �̸��� ����
        msg = '%d:%s:%s\n' % (len(data), f_md5, fname)
        print msg
        fp.write(msg)
        fp.close()
    except :
        import traceback
        print traceback.format_exc()
        pass


def GetDateValue(now) :
    t_y = now.tm_year - 1980
    t_y = (t_y << 9) & 0xFE00
    t_m = (now.tm_mon << 5) & 0x01E0
    t_d = (now.tm_mday) & 0x001F

    return (t_y | t_m | t_d) & 0xFFFF


def GetTimeValue(now) :
    t_h = (now.tm_hour << 11) & 0xF800
    t_m = (now.tm_min << 5) & 0x07E0
    t_s = (now.tm_sec / 2) & 0x001F

    return (t_h | t_m | t_s) & 0xFFFF

# [HEADER                   ][CODE Image][TAILER  ]
# [KAVM][DATE][TIME][Sig Num][Image     ][Sha256x3]

def Func_Pack(filename, id) :
    global line_num

    try :
        Paser_SigMDB(filename, id)

        fname = '%s.c%02d' % (filename, id)
        SigDB2PatBin(fname, line_num)

        fname = '%s.i%02d' % (filename, id)
        SigDB2PatBin(fname, 0)
    except :
        import traceback
        print traceback.format_exc()
        pass

def Paser_SigMDB(file, num) :
    fp = open(SIGDB_FILENAME)

    while 1: 
        lines = fp.readlines(100000) #�޸𸮰� ����ϴ� ������ �� 
        if not lines: 
            break 
        for line in lines: 
            convert(line, num)

    fp.close()

    fname = '%s.c%02d' % (file, num)
    output = open(fname, 'wb')
    #s = pickle.dumps(db_size_pattern, -1)
    s = marshal.dumps(db_size_pattern)
    output.write(s)
    output.close()

    fname = '%s.i%02d' % (file, num)
    output = open(fname, 'wb')
    # s = pickle.dumps(db_vname, -1)
    s = marshal.dumps(db_vname)
    output.write(s)
    output.close()

db_size_pattern = {}
db_vname = []
line_num = 0

def convert(line, num) :
    global db_size_pattern
    global db_vname
    global line_num

    line    = line.strip()
    pattern = line.split(':')

    fsize   = int(pattern[0])
    md5     = pattern[1].decode('hex')
    virname = pattern[2]

    try :
        id_pattern = db_size_pattern[fsize]
    except :
        id_pattern = {}

    id_pattern[md5[0:6]] = [num, line_num] # ���Ϲ�ȣ, ���̷����� ID

    db_size_pattern[fsize] = id_pattern
    line_num += 1

    t = [md5[6:], virname]
    db_vname.append(t)

def SigDB2PatBin(fname, sig_num) :
    shutil.copy (fname, fname+'.bak') # bak ���Ϸ� ����

    # Compress
    fp = open(fname, 'rb')
    buf1 = fp.read()
    fp.close()

    buf2 = zlib.compress(buf1, 9)

    # Add Date and Time
    now = time.gmtime()
    ret_date = GetDateValue(now)
    ret_time = GetTimeValue(now)

    d = struct.pack('<H', ret_date)
    t = struct.pack('<H', ret_time)
    sig_num = struct.pack('<L', long(sig_num))

    # Add MagicID('KAVM')
    buf3 = 'KAVM' + d + t + sig_num + buf2

    sha256 = hashlib.sha256()

    # sha256 hash value is calculated 3 times
    if len(buf3) > 0x4000 :
        sha256hash = buf3[:0x4000]
    else :
        sha256hash = buf3

    for i in range(3): 
        sha256.update(sha256hash)
        sha256hash = sha256.hexdigest()   
        
    buf3 += sha256hash # Add sha256x3 to tail

    # Write file
    fp = open(fname, 'wb')
    fp.write(buf3)
    fp.close()

    print 'Success : %s' % (fname)  

#---------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------
def main() :
    try :
        # �ɼ� �м�
        options, args = ParserOptions()

        PrintLogo()

        # �߸��� �ɼ�?
        if options == None :
            PrintUsage()
            PrintOptions()
            return 0

        print 

        # MD5 ��� �ɼ�
        if options.md5_fname != None : Func_MD5(options.md5_fname)
        elif options.pack_fname != None : Func_Pack(options.pack_fname, options.id_num)
        else :
            PrintUsage()
            PrintOptions()
            return 0

    except :
        pass
    
    return 1

if __name__ == '__main__' :
    main()