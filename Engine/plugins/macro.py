# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import os # ���� ������ ���� import
import zlib
import hashlib
import struct, mmap
import kernel
import kavutil
import glob


def IsPrint(char) :
    c = ord(char)
    if c > 0x20 and c < 0x80 :
        return True
    else :
        return False

def ExtractMacroData_X95M(data) :
    mac_data = None
    data_size = len(data)

    try :
        if data_size < 0x200 : raise SystemError
        if ord(data[0]) != 0x01 : raise SystemError

        mac_pos = struct.unpack('<L', data[10:10+4])[0]
        mac_pos += ( 14L + 14L )
        if data_size < mac_pos : raise SystemError

        t = struct.unpack('<L', data[mac_pos:mac_pos+4])[0]
        mac_pos += t + 28L + 18L - 14L;
        if data_size < mac_pos : raise SystemError

        mac_pos = struct.unpack('<L', data[mac_pos:mac_pos+4])[0]
        mac_pos += 0x3C
        if data_size < mac_pos : raise SystemError

        # ��ũ�� ���� ��ġ���� ����
        if ord(data[mac_pos]) != 0xFE or ord(data[mac_pos+1]) != 0xCA :
            raise SystemError

        # ��ũ�� �ҽ� �ڵ��� �� �� ���
        mac_lines = struct.unpack('<H', data[mac_pos+4:mac_pos+6])[0]
        if mac_lines == 0 : raise SystemError 

        mac_pos = mac_pos + 4L + (mac_lines * 12L)
        if data_size < mac_pos : raise SystemError
        
        mac_len = struct.unpack('<L', data[mac_pos+6:mac_pos+10])[0]
        mac_pos += 10

        # print 'ok :', hex(mac_pos), mac_lines, mac_len

        # ��ũ�� ��� ���� ����
        if data_size < (mac_pos + mac_len) : raise SystemError
        mac_data = data[mac_pos:mac_pos + mac_len]

    except :
        pass

    return mac_data

def GetMD5_X95M(data) :
    ret = None

    try :
        max = 0
        buf = ''

        for i in range(len(data)) :
            c = data[i]
            if IsPrint(c) :
                max += 1
            else :
                if max > 3 :
                    # print data[i-max:i] # ���� ������ ���� (sigtool)
                    buf += data[i-max:i]
                max = 0

        md5 = hashlib.md5()
        md5.update(buf)
        fmd5 = md5.hexdigest().decode('hex')

        # print '%s:%s:%s:' % (len(buf), md5.hexdigest(), len(data)) # ���� ���� (sigtool)
        ret = (len(buf), fmd5, len(data))
    except :
        import traceback
        print traceback.format_exc()
        pass

    return ret



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
        try :
            self.plugins = plugins
            self.x95m_ptn   = []
            self.x95m_iptn       = {}
            self.__signum__ = 0
            self.__date__   = 0
            self.__time__   = 0

            max_date = 0
            vdb = kavutil.VDB()

            flist = glob.glob(plugins + os.sep +'x95m.c*')
            for i in range(len(flist)) :
                fname = flist[i]
                
                # ���� �ε�
                self.x95m_ptn.append(vdb.Load(fname))

                if self.x95m_ptn[i] == None :
                    return 1 # ���� �ε� ����

                self.__signum__ += vdb.GetSigNum()

                # �ֽ� ��¥ ���ϱ�
                t_d = vdb.GetDate()
                t_t = vdb.GetTime()

                t_date = (t_d << 16) + t_t
                if max_date < t_date :
                    self.__date__ = t_d
                    self.__time__ = t_t
                    max_date = t_date

            return 0
        except :
            import traceback
            print traceback.format_exc()

            return 1

    #-----------------------------------------------------------------
    # uninit(self)
    # ��� ���� ����� ����ȭ �۾��� �����Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) : # ��� ��� ����ȭ
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
        ret = None
        scan_state = kernel.NOT_FOUND
        ret_value = {}
        ret_value['result']     = False # ���̷��� �߰� ����
        ret_value['virus_name'] = ''    # ���̷��� �̸�
        ret_value['scan_state'] = kernel.NOT_FOUND # 0:����, 1:����, 2:�ǽ�, 3:���
        ret_value['virus_id']   = -1    # ���̷��� ID

        try :
            section_name = scan_file_struct['deep_filename']

            # _VBA_PROJECT/xxxx �� �����ϴ� ��Ʈ���� ����95 ��ũ�ΰ� �����Ѵ�.
            if section_name.find(r'_VBA_PROJECT/') != -1 :
                data = mmhandle[:] # ���� ��ü ����
                ret = self.__ScanVirus_X95M__(data)

            if ret != None :
                scan_state, s, i_num, i_list = ret

                # ���̷��� �̸� ����
                if s[0:2] == 'V.' :
                    s = 'Virus.MSExcel.' + s[2:]
                elif s[0:2] == 'J.' :
                    s = 'Joke.MSExcel.' + s[2:]

                # �Ǽ��ڵ� ������ ���ٸ� ��� ���� �����Ѵ�.
                ret_value['result']     = True # ���̷��� �߰� ����
                ret_value['virus_name'] = s    # ���̷��� �̸�
                ret_value['scan_state'] = scan_state # 0:����, 1:����, 2:�ǽ�, 3:���
                ret_value['virus_id']   = 0    # ���̷��� ID
                return ret_value            
        except :
            pass

        # �Ǽ��ڵ带 �߰����� �������� �����Ѵ�.
        return ret_value

    def __ScanVirus_X95M__(self, data) :
        ret = None

        try :
            mac_data = ExtractMacroData_X95M(data)
            if mac_data == None : raise SystemError

            hash_data = GetMD5_X95M(mac_data)

            fsize    = hash_data[0] # md5�� ������ ������ ũ��
            fmd5     = hash_data[1] # md5
            mac_size = hash_data[2] # ���� ��ũ�� ũ��

            # ���� ��
            i_num = -1

            for i in range(len(self.x95m_ptn)) :
                vpattern = self.x95m_ptn[i]

                try :
                    t = vpattern[fsize] # ���� �߿� ���� ũ��� �� MD5�� �����ϳ�?

                    # MD5�� 6�ڸ� ������ ��ġ�ϴ��� ����
                    id = t[fmd5[0:6]]

                    # ������ 10�ڸ��� ���ؾ� ��
                    i_num = id[0]   # x95m.iXX ���Ͽ�..
                    i_list = id[1]  # ���° ����Ʈ���� �˰� ��
                except :
                    pass

                if i_num != -1 : # MD5 6�ڸ��� ��ġ�ϴ� ���� �߰� �Ǿ��ٸ�
                    try :
                        e_vlist = self.x95m_iptn[i_num]
                    except :
                        fname = '%s%sx95m.i%02d' % (self.plugins, os.sep, i_num)
                        vdb = kavutil.VDB() # ���� �ε�
                        e_vlist = vdb.Load(fname)

                    if e_vlist != None :
                        self.x95m_iptn[i_num] = e_vlist

                        p_md5_10 = e_vlist[i_list][0] # MD5 10�ڸ�
                        p_mac_size = int(e_vlist[i_list][1]) # ��ũ�� ũ�� 
                        p_vname = e_vlist[i_list][2]  # ���̷��� �̸�

                        if (p_md5_10 == fmd5[6:]) and (p_mac_size == mac_size) : # ��� ��ġ
                            ret = (kernel.INFECTED, p_vname, i_num, i_list)
                        elif p_md5_10 == fmd5[6:] : # md5�� ��ġ
                            s = p_vname + '.Gen'
                            ret = (kernel.SUSPECT, s, i_num, i_list)
        except :
            pass

        return ret

    #-----------------------------------------------------------------
    # disinfect(self, filename, malwareID)
    # �Ǽ��ڵ带 ġ���Ѵ�.
    # ���ڰ� : filename   - ���� �̸�
    #        : malwareID  - ġ���� �Ǽ��ڵ� ID
    # ���ϰ� : �Ǽ��ڵ� ġ�� ����
    #-----------------------------------------------------------------
    def disinfect(self, filename, malwareID) : # �Ǽ��ڵ� ġ��
        try :
            '''
            # �Ǽ��ڵ� ���� ������� ���� ID ���� 0�ΰ�?
            if malwareID == 0 : 
                os.remove(filename) # ���� ����
                return True # ġ�� �Ϸ� ����
            '''
        except :
            pass

        return False # ġ�� ���� ����

    #-----------------------------------------------------------------
    # listvirus(self)
    # ����/ġ�� ������ �Ǽ��ڵ��� ����� �˷��ش�.
    #-----------------------------------------------------------------
    def listvirus(self) : # ���� ������ �Ǽ��ڵ� ���
        vlist = [] # ����Ʈ�� ���� ����
        vlist.append('Virus.MSExcel.Laroux.A') 
        return vlist

    #-----------------------------------------------------------------
    # getinfo(self)
    # ��� ���� ����� �ֿ� ������ �˷��ش�. (����, ������...)
    #-----------------------------------------------------------------
    def getinfo(self) :
        info = {} # ������ ���� ����
        info['author'] = 'Kei Choi' # ������
        info['version'] = '1.0'     # ����
        info['title'] = 'Macro Engine' # ���� ����
        info['kmd_name'] = 'macro' # ���� ���ϸ�

        # ���� ������¥�� �ð��� ���ٸ� ���� �ð����� �ڵ� ����
        info['date']    = self.__date__   # ���� ���� ��¥ 
        info['time']    = self.__time__   # ���� ���� �ð� 
        info['sig_num'] = self.__signum__ # ���� ��
        return info

