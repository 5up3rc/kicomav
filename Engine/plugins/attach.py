# -*- coding:utf-8 -*-

"""
Copyright (C) 2013 Nurilab.

Author: Kei Choi(hanul93@gmail.com)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.
"""

__revision__ = '$LastChangedRevision: 1 $'
__author__   = 'Kei Choi'
__version__  = '1.0.0.%d' % int( __revision__[21:-2] )
__contact__  = 'hanul93@gmail.com'

import mmap
import tempfile
import kernel


#---------------------------------------------------------------------
# KavMain Ŭ����
# Ű�޹�� ���� ������� ��Ÿ���� Ŭ�����̴�.
# �� Ŭ������ ������ ��� ���� Ŀ�� ��⿡�� �ε����� �ʴ´�.
#---------------------------------------------------------------------
class KavMain :
    #-----------------------------------------------------------------
    # init(self, plugins)
    # ��� ���� ����� �ʱ�ȭ �۾��� �����Ѵ�.
    #-----------------------------------------------------------------
    def init(self, plugins) : # ��� ��� �ʱ�ȭ
        return 0

    #-----------------------------------------------------------------
    # uninit(self)
    # ��� ���� ����� ����ȭ �۾��� �����Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) : # ��� ��� ����ȭ
        return 0
    
    #-----------------------------------------------------------------
    # getinfo(self)
    # ��� ���� ����� �ֿ� ������ �˷��ش�. (����, ������...)
    #-----------------------------------------------------------------
    def getinfo(self) :
        info = {} # ������ ���� ����
        info['author'] = __author__ # ������
        info['version'] = __version__     # ����
        info['title'] = 'Attach Engine' # ���� ����
        info['kmd_name'] = 'attach' # ���� ���ϸ�
        return info

    #-----------------------------------------------------------------
    # arclist(self, scan_file_struct, format)
    # ���� ���� ������ ����� ���ϸ��� ����Ʈ�� �����Ѵ�.
    #-----------------------------------------------------------------
    def arclist(self, scan_file_struct, format) :
        file_scan_list = [] # �˻� ��� ������ ��� ����
        deep_name = ''

        try :
            # �̸� �м��� ���� �����߿� �߰� ������ �ִ°�?
            fformat = format['ff_attach']

            filename = scan_file_struct['real_filename']
            deep_name = scan_file_struct['deep_filename']

            pos = fformat['Attached_Pos']
            if pos <= 0 : 
                raise SystemError

            name = 'Attached'
            arc_name = 'arc_attach!%s' % pos

            file_info = {}  # ���� �Ѱ��� ����

            if len(deep_name) != 0 :
                dname = '%s/%s' % (deep_name, name)
            else :
                dname = '%s' % (name)

            file_info['is_arc'] = True # ���� ����
            file_info['arc_engine_name'] = arc_name # ���� ���� ���� ���� ID
            file_info['arc_filename'] = filename # ���� ���� ����
            file_info['arc_in_name'] = name #�������� ��� ����
            file_info['real_filename'] = '' # �˻� ��� ����
            file_info['deep_filename'] = dname  # ���� ������ ���θ� ǥ���ϱ� ���� ���ϸ�
            file_info['display_filename'] = scan_file_struct['display_filename'] # ��¿�

            file_scan_list.append(file_info)
        except :
            pass

        return file_scan_list

    #-----------------------------------------------------------------
    # unarc(self, scan_file_struct)
    # �־��� ����� ���ϸ����� ������ �����Ѵ�.
    #-----------------------------------------------------------------
    def unarc(self, scan_file_struct) :
        fp = None
        mm = None

        try :
            if scan_file_struct['is_arc'] != True : 
                raise SystemError

            arc_id = scan_file_struct['arc_engine_name']
            if arc_id[0:10] != 'arc_attach' :
                raise SystemError

            pos = int(arc_id[11:]) # ÷�ε� ������ ��ġ ���
            if pos <= 0 : 
                raise SystemError

            arc_name = scan_file_struct['arc_filename']
            filename = scan_file_struct['arc_in_name']

            # ÷�� ������ ���� ���� ����
            fp = open(arc_name, 'rb') 
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)

            data = mm[pos:]

            mm.close()
            fp.close()

            mm = None
            fp = None

            # ������ �����Ͽ� �ӽ� ������ ����
            rname = tempfile.mktemp(prefix='ktmp')
            fp = open(rname, 'wb')
            fp.write(data)
            fp.close()

            scan_file_struct['real_filename'] = rname

            return scan_file_struct
        except :
            pass

        if mm != None : mm.close()
        if fp != None : fp.close()

        return None
