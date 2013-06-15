# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import os # ���� ������ ���� import
import kernel

#---------------------------------------------------------------------
# KavMain Ŭ����
# Ű�޹�� ���� ������� ��Ÿ���� Ŭ�����̴�.
# �� Ŭ������ ������ ��� ���� Ŀ�� ��⿡�� �ε����� �ʴ´�.
#---------------------------------------------------------------------
class KavMain :
    #-----------------------------------------------------------------
    # init(self)
    # ��� ���� ����� �ʱ�ȭ �۾��� �����Ѵ�.
    #-----------------------------------------------------------------
    def init(self) : # ��� ��� �ʱ�ȭ
        self.virus_name = 'Dummy-Test-File (not a virus)' # �����ϴ� �Ǽ��ڵ� �̸�
        # �Ǽ��ڵ� ���� ���
        self.dummy_pattern = 'Dummy Engine test file - KICOM Anti-Virus Project, 2012, Kei Choi'
        return 0

    #-----------------------------------------------------------------
    # uninit(self)
    # ��� ���� ����� ����ȭ �۾��� �����Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) : # ��� ��� ����ȭ
        del self.virus_name
        del self.dummy_pattern
        return 0
    
    #-----------------------------------------------------------------
    # scan(self, filehandle, filename)
    # �Ǽ��ڵ带 �˻��Ѵ�.
    # ���ڰ� : mmhandle         - ���� mmap �ڵ�
    #        : scan_file_struct - ���� ����ü
    #        : format           - �̸� �м��� ���� ����
    # ���ϰ� : (�Ǽ��ڵ� �߰� ����, �Ǽ��ڵ� �̸�, �Ǽ��ڵ� ID) ���
    #-----------------------------------------------------------------
    def scan(self, mmhandle, scan_file_struct, format) :
        ret_value = {}
        ret_value['result']     = False # ���̷��� �߰� ����
        ret_value['virus_name'] = ''    # ���̷��� �̸�
        ret_value['scan_state'] = kernel.NOT_FOUND     # 0:����, 1:����, 2:�ǽ�, 3:���
        ret_value['virus_id']   = -1    # ���̷��� ID

        try :
            # �̸� �м��� ���� �����߿� Dummy ������ �ִ°�?
            fformat = format['ff_dummy']

            # �̸� �м��� ���� ���˿� ũ�Ⱑ 65Byte?
            if fformat['size'] != len(self.dummy_pattern) :
                raise SystemError

            # ������ ���� �Ǽ��ڵ� ���ϸ�ŭ ���Ͽ��� �д´�.
            filename = scan_file_struct['real_filename']
            fp = open(filename)
            buf = fp.read(len(self.dummy_pattern)) # ������ 65 Byte ũ��
            fp.close()

            # �Ǽ��ڵ� ������ ���Ѵ�.
            if buf == self.dummy_pattern :
                # �Ǽ��ڵ� ������ ���ٸ� ��� ���� �����Ѵ�.
                ret_value['result']     = True            # ���̷��� �߰� ����
                ret_value['virus_name'] = self.virus_name # ���̷��� �̸�
                ret_value['scan_state'] = kernel.INFECTED# 0:����, 1:����, 2:�ǽ�, 3:���
                ret_value['virus_id']   = 0               # ���̷��� ID
                return ret_value
        except :
            pass

        # �Ǽ��ڵ带 �߰����� �������� �����Ѵ�.
        return ret_value

    #-----------------------------------------------------------------
    # disinfect(self, filename, malwareID)
    # �Ǽ��ڵ带 ġ���Ѵ�.
    # ���ڰ� : filename   - ���� �̸�
    #        : malwareID  - ġ���� �Ǽ��ڵ� ID
    # ���ϰ� : �Ǽ��ڵ� ġ�� ����
    #-----------------------------------------------------------------
    def disinfect(self, filename, malwareID) : # �Ǽ��ڵ� ġ��
        try :
            # �Ǽ��ڵ� ���� ������� ���� ID ���� 0�ΰ�?
            if malwareID == 0 : 
                os.remove(filename) # ���� ����
                return True # ġ�� �Ϸ� ����
        except :
            pass

        return False # ġ�� ���� ����

    #-----------------------------------------------------------------
    # listvirus(self)
    # ����/ġ�� ������ �Ǽ��ڵ��� ����� �˷��ش�.
    #-----------------------------------------------------------------
    def listvirus(self) : # ���� ������ �Ǽ��ڵ� ���
        vlist = [] # ����Ʈ�� ���� ����
        vlist.append(self.virus_name) # �����ϴ� �Ǽ��ڵ� �̸� ���
        return vlist

    #-----------------------------------------------------------------
    # getinfo(self)
    # ��� ���� ����� �ֿ� ������ �˷��ش�. (����, ������...)
    #-----------------------------------------------------------------
    def getinfo(self) :
        info = {} # ������ ���� ����
        info['author'] = 'Kei Choi' # ������
        info['version'] = '1.0'     # ����
        info['title'] = 'Dummy Scan Engine' # ���� ����
        info['kmd_name'] = 'dummy' # ���� ���ϸ�
        return info

    #-----------------------------------------------------------------
    # format(self, mmhandle, filename)
    # Dummy ���� ���� �м����̴�.
    #-----------------------------------------------------------------
    def format(self, mmhandle, filename) :
        try :
            fformat = {} # ���� ������ ���� ����

            mm = mmhandle
            if mm[0:5] == 'Dummy' : # ��� üũ
                fformat['size'] = len(mm) # ���� �ֿ� ���� ����

                ret = {}
                ret['ff_dummy'] = fformat
                return ret
        except :
            pass

        return None