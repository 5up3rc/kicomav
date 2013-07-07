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


import struct
import mmap

UPX_NRV2B = '\x11\xdb\x11\xc9\x01\xdb\x75\x07\x8b\x1e\x83\xee\xfc'
UPX_NRV2D = '\x83\xf0\xff\x74\x78\xd1\xf8\x89\xc5\xeb\x0b\x01\xdb'
UPX_NRV2E = '\xeb\x52\x31\xc9\x83\xe8\x03\x72\x11\xc1\xe0\x08\x8a'
UPX_LZMA1 = '\x56\x83\xc3\x04\x53\x50\xc7\x03\x03\x00\x02\x00\x90'
UPX_LZMA2 = '\x56\x83\xc3\x04\x53\x50\xc7\x03\x03\x00\x02\x00\x90'

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
    # getinfo(self)
    # ��� ���� ����� �ֿ� ������ �˷��ش�. (����, ������...)
    #-----------------------------------------------------------------
    def getinfo(self) :
        info = {} # ������ ���� ����
        info['author'] = __author__    # ������
        info['version'] = __version__  # ����
        info['title'] = 'UPX Unpacker' # ���� ����
        info['kmd_name'] = 'upx'       # ���� ���ϸ�
        return info

    #-----------------------------------------------------------------
    # arclist(self, scan_file_struct, format)
    # ���� �м����̴�.
    #-----------------------------------------------------------------
    def arclist(self, scan_file_struct, format) :
        fp = None
        mm = None
        file_scan_list = [] # �˻� ��� ������ ��� ����
        deep_name = ''

        try :
            # �̸� �м��� ���� �����߿� PE ������ �ִ°�?
            fformat   = format['ff_pe']
            pe_format = fformat['pe']
            ep_foff   = pe_format['EntryPointRaw']

            filename = scan_file_struct['real_filename']
            deep_name = scan_file_struct['deep_filename']

            fp = open(filename, 'rb')
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)

            if   mm[ep_foff+0x69:ep_foff+0x69+13] == UPX_NRV2B : arc_name = 'arc_upx!nrv2b'
            elif mm[ep_foff+0x71:ep_foff+0x71+13] == UPX_NRV2B : arc_name = 'arc_upx!nrv2b'
            elif mm[ep_foff+0x69:ep_foff+0x69+13] == UPX_NRV2D : arc_name = 'arc_upx!nrv2d'
            elif mm[ep_foff+0x71:ep_foff+0x71+13] == UPX_NRV2D : arc_name = 'arc_upx!nrv2d'
            elif mm[ep_foff+0x69:ep_foff+0x69+13] == UPX_NRV2E : arc_name = 'arc_upx!nrv2e'
            elif mm[ep_foff+0x71:ep_foff+0x71+13] == UPX_NRV2E : arc_name = 'arc_upx!nrv2e'
            else :
                raise SystemError

            name = 'UPX'

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

        if mm != None : mm.close()
        if fp != None : fp.close()

        return file_scan_list