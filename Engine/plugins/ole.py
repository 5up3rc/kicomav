# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

# EXTRA BBD ���� ����
import struct

#---------------------------------------------------------------------
# GetDword_file(fp, offset)
# GetWord_file(fp, offset)
# GetRead_file(fp, offset, size)
# ���Ͽ��� ������ ũ�⸸ŭ �о�´�
#---------------------------------------------------------------------
# ���� �����Ϳ��� 4Byte �� ����
def GetDword_file(fp, offset) :
  s = GetRead_file(fp, offset, 4)
  return struct.unpack("<L", s[0:4])[0]

# ���� �����Ϳ��� 2Byte �� ����
def GetWord_file(fp, offset) :
  s = GetRead_file(fp, offset, 2)
  return struct.unpack("<H", s[0:2])[0]

# ���� �����Ϳ��� Ư�� ũ�⸸ŭ �б�
def GetRead_file(fp, offset, size) :
  fp.seek(offset)
  return fp.read(size)

#---------------------------------------------------------------------
# GetDword(s, offset)
# GetWord(s, offset)
# GetRead(s, offset, size)
# ���ۿ��� ������ ũ�⸸ŭ �о�´�
#---------------------------------------------------------------------
# ���� �����Ϳ��� 4Byte �� ����
def GetDword(s, offset) :
  return struct.unpack("<L", s[offset:offset+4])[0]

# ���� �����Ϳ��� 2Byte �� ����
def GetWord(s, offset) :
  return struct.unpack("<H", s[offset:offset+2])[0]

# ���� �����Ϳ��� Ư�� ũ�⸸ŭ �б�
def GetRead(s, offset, size) :
  return s[offset:offset+size]


#---------------------------------------------------------------------
# OLE Ŭ����
#---------------------------------------------------------------------
class OLE :
    bbd_list      = []
    bbd_list_pos  = []
    sbd_list      = []
    sbd_list_pos  = []
    root_list     = []
    root_list_pos = []
    pps_list      = []
    sdb_list     = []
    sdb_list_pos = []
    deep  = 0
    Error = -1
    bbd = ""
    sbd = ""

    def __init__ (self, filename) :
        self.olefile = filename

    def parse(self) :
        try :
            self.fp = open(self.olefile, 'rb')
            
            # OLE ���� �ñ׳�ó üũ
            if GetDword_file(self.fp, 0x0) != 0xe011cfd0L or GetDword_file(self.fp, 0x4) != 0xe11ab1a1L:
                return -1

            # BBD �� ������ŭ BDB �б�
            num_of_bbd_blocks = GetDword_file(self.fp, 0x2c)


            if num_of_bbd_blocks > 109 :
                j = 109
            else :
                j = num_of_bbd_blocks

            for i in range(j) :
                self.bbd_list.append(GetDword_file(self.fp, 0x4c + (i*4)))
                self.bbd_list_pos.append((self.bbd_list[i]+1) << 9)

            # XBBD �� ó��
            num_of_Xbbd_blocks = GetDword_file(self.fp, 0x48)
            xbbd_start         = GetDword_file(self.fp, 0x44)

            if xbbd_start != 0xFFFFFEL :
                xbbd = ""
                val = xbbd_start

                for i in range(num_of_Xbbd_blocks) :
                    buf = GetRead_file(self.fp, (val+1)<<9, 0x200)
                    xbbd += buf[0:0x1FC]
                    val = GetDword(buf, 0x1FC)

                for i in range(num_of_bbd_blocks-109) :
                    val = GetDword(xbbd, (i*4))
                    self.bbd_list.append(val)
                    self.bbd_list_pos.append((val+1) << 9)

            # BBD ����
    #       bbd = ""
            for i in range(num_of_bbd_blocks) :
                self.bbd += GetRead_file(self.fp, self.bbd_list_pos[i], 0x200)

            # SBD �� ������ŭ SBD �б�
            sbd_startblock = GetDword_file(self.fp, 0x3c)
            num_of_sbd_blocks = GetDword_file(self.fp, 0x40)

            self.sbd_list.append(sbd_startblock)
            self.sbd_list_pos.append((sbd_startblock+1)<<9)

            i = sbd_startblock
            while True :
                val = GetDword(self.bbd, i*4)
                if val == 0xFFFFFFFEL :
                    break
                self.sbd_list.append(val)
                self.sbd_list_pos.append((val+1)<<9)
                i = val

            # SBD ����
    #       sbd = ""
            for i in range(num_of_sbd_blocks) :
                self.sbd += GetRead_file(self.fp, self.sbd_list_pos[i], 0x200)


            # Root Entry ��ô�ϱ�
            root_startblock = GetDword_file(self.fp, 0x30)

            self.root_list.append(root_startblock)
            self.root_list_pos.append((root_startblock+1)<<9)

            i = root_startblock
            while True :
                val = GetDword(self.bbd, i*4)
                if val == 0xfffffffeL :
                    break
                self.root_list.append(val)
                self.root_list_pos.append((val+1)<<9)
                i = val  

            # root ����
            root = ""
            for i in range(len(self.root_list_pos)) :
                root += GetRead_file(self.fp, self.root_list_pos[i], 0x200)

            # PPS ����
            for i in range(len(self.root_list_pos) * 4) :
                pps = {}
                pps_buf = GetRead(root, i*0x80, 0x80)
                # {'Name':'Root Entry', NameSize:16, Type:5, Prev:0xFFFFFFFF, Next:0xFFFFFFFF, Dir:0x3, StartBlock:0x3, Size:0x1000]
                pps['Name']       = pps_buf[0:GetWord(pps_buf, 0x40)]
                pps['NameSize']   = GetWord(pps_buf, 0x40)
                pps['Type']       = GetWord(pps_buf, 0x42)
                pps['Prev']       = GetDword(pps_buf, 0x44)
                pps['Next']       = GetDword(pps_buf, 0x48)
                pps['Dir']        = GetDword(pps_buf, 0x4c)
                pps['StartBlock'] = GetDword(pps_buf, 0x74)
                pps['Size']       = GetDword(pps_buf, 0x78)

                self.pps_list.append(pps)

            # SDB ����
            sdb_startblock = self.pps_list[0]['StartBlock']

            self.sdb_list.append(sdb_startblock)
            self.sdb_list_pos.append((sdb_startblock+1)<<9)

            i = sdb_startblock
            while True :
                val = GetDword(self.bbd, i*4)
                if val == 0xfffffffeL :
                    break
                self.sdb_list.append(val)
                self.sdb_list_pos.append((val+1)<<9)
                i = val  

            self.Error = 0
        except :
            pass

        self.fp.close()
        return self.Error

    # PPS Ʈ���� ��´�
    def GetPPSList(self) :
        return self.pps_list

    # PPS Ʈ�� ����ϱ�
    def PrintTree(self, node=0, prefix="") :
        if self.Error == -1 :
            return -1

        print ("    %02d : " + "%s" + "%s") % (node, self.deep*"   ", self.pps_list[node]['Name'][0:self.pps_list[node]['NameSize']:2])

        if self.pps_list[node]['Dir'] != 0xFFFFFFFFL :
            self.deep += 1
            self.PrintTree(self.pps_list[node]['Dir'])
            self.deep -= 1

        if self.pps_list[node]['Prev'] != 0xFFFFFFFFL :
            self.PrintTree(self.pps_list[node]['Prev'])

        if self.pps_list[node]['Next'] != 0xFFFFFFFFL :
            self.PrintTree(self.pps_list[node]['Next'])

        return 0

    # PPS�� �����Ѵ�
    def DumpPPS(self, node, fname) :
        if self.Error == -1 :
            return -1

        size = self.pps_list[node]['Size']
        sb = self.pps_list[node]['StartBlock'] 

        if size < 0x1000 :
            block_depot = self.sbd
            pps_size    = 0x40
        else :
            block_depot = self.bbd
            pps_size    = 0x200

        bd_list = []
        bd_list.append(sb);

        i = sb
        while True :
            val = GetDword(block_depot, i*4)
            if val == 0xFFFFFFFEL :
                break
            bd_list.append(val)
            i = val

        bd_list_pos = []

        for i in range(len(bd_list)) :
            if size < 0x1000 :
                v1 = bd_list[i] / 8
                v2 = bd_list[i] % 8
                bd_list_pos.append(self.sdb_list_pos[v1] + (0x40 * v2))
            else :
                bd_list_pos.append((bd_list[i]+1)<<9)

        fp1 = open(fname, "wb")

        for i in range(len(bd_list)) :
            pps_buf = GetRead_file(self.fp, bd_list_pos[i], pps_size)
            fp1.write(pps_buf)

        fp1.truncate(size)
        fp1.close()

        return 0



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
    def init(self) :
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
        info['author'] = 'Kei Choi' # ������
        info['version'] = '1.0'     # ����
        info['title'] = 'OLE Engine' # ���� ����
        return info
