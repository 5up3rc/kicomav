# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import zlib
import hashlib
import StringIO
import marshal
import imp
import sys
import os
import types
import mmap
import traceback

#---------------------------------------------------------------------
# Engine Ŭ����
#---------------------------------------------------------------------
class Engine :
    def __init__(self) :
        self.kmd_list = []
        self.mod_list = []
    
    # plugins ������ kmd ����� �ε��Ѵ�.
    def SetPlugings(self, plugins) :
        ret = False
        self.ckmd = KMD()

        try :
            if len(self.kmd_list) == 0 : # �켱���� list ������ ���ٸ�
                # kmd �ε� �켱���� ����Ʈ�� ���� kmd ���Ͽ��� ����Ʈ Ȯ��
                self.kmd_list = self.ckmd.GetList(plugins) # kicom.kmd ���� �ε�
                if len(self.kmd_list) == 0 :      # ��� ���� ������ ����
                    raise SystemError 

            # kmd �ε� �켱���� ����Ʈ ������ ���� �ε�
            if len(self.mod_list) == 0 :
                self.mod_list = self.ckmd.Import(plugins, self.kmd_list)
            
            ret = True
        except :
            print traceback.format_exc()
            pass

        return ret

    def CreateInstance(self) :
        ei = EngineInstance()
        ret = ei.SetModuleList(self.ckmd, self.mod_list)

        if ret == 0 :
            return ei
        else :
            return None
        
#---------------------------------------------------------------------
# EngineInstance Ŭ����
#---------------------------------------------------------------------
class EngineInstance :
    def __init__(self) :
        self.modules        = []
        self.KMD_AntiVirus  = []
        self.KMD_Decompress = []
        self.KMD_FileFormat = []

    def SetModuleList(self, ckmd, mod_list) :
        try :
            for m in mod_list :
                # ���� �ε� �Ǿ����� ��� ���� ����Ʈ�� �߰�
                mod = ckmd.ExecKavMain(m)
                if mod != None :
                    self.modules.append(mod)

            # �ε��� ����� �ϳ��� ������ ����
            if len(self.modules) == 0 : 
                raise SystemError 
        except :
            return 1
            
        return 0

    #-----------------------------------------------------------------
    # init(self)
    # Ű�޹�� ������ �ʱ�ȭ �Ѵ�.
    # ���ϰ� : ���� ���� (True, False)
    #-----------------------------------------------------------------
    def init(self) :
        try :
            # ��� ��� ���� ����� init ��� �Լ� ȣ��
            for mod in self.modules :
                if dir(mod).count('init') != 0 : # API ����
                    ret_init = mod.init() # ȣ��
                    if ret_init != 0 :
                        raise SystemError
        except :
            return False
            
        return True        

    #-----------------------------------------------------------------
    # uninit(self)
    # Ű�޹�� ������ ����ȭ �Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) :
        # ��� ���� ����� uninit ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('uninit') != 0 : # API ����
                ret_uninit = mod.uninit()

    #-----------------------------------------------------------------
    # scan(self, filename)
    # Ű�޹�� ������ �Ǽ��ڵ带 �����Ѵ�.
    #-----------------------------------------------------------------
    def scan(self, filename) :
        ret = False

        try :
            fp = open(filename, 'rb')
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
            
            # ��� ���� ����� scan ��� �Լ� ȣ��
            for mod in self.modules :
                if dir(mod).count('scan') != 0 : # API ����
                    ret, vname, id = mod.scan(mm, filename)
                    if ret == True : # �Ǽ��ڵ� �߰��̸� �˻� �ߴ�
                        break

            mm.close()
            fp.close()

            if ret == True :
                return ret, self.modules.index(mod), vname, id
        except :
            pass

        return False, -1, '', -1

    #-----------------------------------------------------------------
    # disinfect(self, filename, modID, virusID)
    # Ű�޹�� ������ �Ǽ��ڵ带 ġ���Ѵ�.
    #-----------------------------------------------------------------
    def disinfect(self, filename, modID, virusID) :
        ret_disinfect = False

        try :
            mod = self.modules[modID]
            if dir(mod).count('disinfect') != 0 : # API ����
                ret_disinfect = mod.disinfect(filename, virusID)

        except :
            pass

        return ret_disinfect

    #-----------------------------------------------------------------
    # getinfo(self)
    # Ű�޹�� ������ �����ϴ� �Ǽ��ڵ� �̸��� �����Ѵ�.
    #-----------------------------------------------------------------
    def getinfo(self) :
        ret = []

        # ��� ���� ����� getinfo ��� �Լ� ȣ��
        for mod in self.modules :
            if dir(mod).count('getinfo') != 0 : # API ����
                ret_getinfo = mod.getinfo()
                ret.append(ret_getinfo)

        return ret

    #-----------------------------------------------------------------
    # listvirus(self, *callback)
    # Ű�޹�� ������ �����ϴ� �Ǽ��ڵ� �̸��� �����Ѵ�.
    #-----------------------------------------------------------------
    def listvirus(self, *callback) :
        # �������� Ȯ��
        argc = len(callback)

        if argc == 0 : # ���ڰ� ������
            cb = None
        elif argc == 1 : # callback �Լ��� �����ϴ��� üũ
            cb = callback[0]
        else : # ���ڰ� �ʹ� ������ ����
            return []

        # ��� ���� ����� listvirus ��� �Լ� ȣ��
        ret = []

        for mod in self.modules :
            if dir(mod).count('listvirus') != 0 : # API ����
                ret_listvirus = mod.listvirus()

                # callback �Լ��� �ִٸ� 
                # callback �Լ� ȣ��
                if type(cb) is types.FunctionType :
                    cb(ret_listvirus)
                # callback �Լ��� ���ٸ� 
                # �Ǽ��ڵ� �̸��� ����Ʈ�� ����
                else :
                    ret += ret_listvirus

        # callback �Լ� ������ ������ �Ǽ��ڵ� ����Ʈ�� ����
        if argc == 0 :
            return ret


#---------------------------------------------------------------------
# KMD Ŭ����
#---------------------------------------------------------------------
class KMD :     
    def GetList(self, plugins) :
        kmd_list = []

        try :
            # kicom.kmd ������ ��ȣȭ
            ret, buf = self.Decrypt(plugins + os.sep + 'kicom.kmd')

            if ret == True : # ����
                msg = StringIO.StringIO(buf) # ���� IO �غ�

                while 1 :
                    # ���� �� ���� �о� ����Ű ����
                    line = msg.readline().strip()
                    if line.find('.kmd') != -1 : # kmd Ȯ���ڰ� �����Ѵٸ�
                        kmd_list.append(line) # kmd ���� ����Ʈ�� �߰�
                    else :
                        break
        except :
            print traceback.format_exc()
            pass
        
        return kmd_list # kmd ���� ����Ʈ ����  

    def Decrypt(self, fname) :
        try : # ���ܰ� �߻��� ���ɼ��� ���� ó��
            fp = open(fname, 'rb') # kmd ���� �б�
            buf = fp.read()
            fp.close()

            f_md5hash = buf[len(buf)-32:] # ���� ���ʿ��� MD5 �ؽ� �� �и�

            md5 = hashlib.md5()

            md5hash = buf[0:len(buf)-32] # ���� ���� 32Byte�� ������ ������ ����
            for i in range(3): # MD5 �ؽ� ���� 3�� �������� ���ϱ�
                md5.update(md5hash)
                md5hash = md5.hexdigest()

            if f_md5hash != md5hash:
                return False, '' # ����

            buf2 = buf[4:len(buf)-32] # KAVM ��� ����

            buf3 =""
            for i in range(len(buf2)):  # buf2 ũ�⸸ŭ...
                c = ord(buf2[i]) ^ 0xFF #��0xFF�� XOR ��ȣȭ �Ѵ�
                buf3 += chr(c)

            buf4 = zlib.decompress(buf3) # ���� ����
            
            return True, buf4 # kmd ��ȣȭ ���� �׸��� ��ȣȭ�� ���� ����
        except : # ���� �߻�
            print traceback.format_exc()
            return False, '' # ����     
    
    def Import(self, plugins, kmd_list) :
        mod_list = []
        
        for kmd in kmd_list :
            ret_kmd, buf = self.Decrypt(plugins + os.sep + kmd)
            if ret_kmd == True :
                ret_imp, mod = self.LoadModule(kmd.split('.')[0], buf)
                if ret_imp == True :
                    mod_list.append(mod)
                    
        return mod_list
        
    def LoadModule(self, kmd_name, buf) :
        try :
            code = marshal.loads(buf[8:]) # ���۸� ������ ������ ����ȭ �� ���ڿ��� ��ȯ
            module = imp.new_module(kmd_name) # ���ο� ��� ����
            exec(code, module.__dict__) # ����ȭ �� ���ڿ��� �������Ͽ� ���� ����
            sys.modules[kmd_name] = module # �������� ��밡���ϰ� ���
            return True, module
        except :
            return False, None

    def ExecKavMain(self, module) :
        obj = None

        # �ε��� ��⿡�� KavMain�� �ִ��� �˻�
        # KavMain�� �߰ߵǾ����� Ŭ������ �ν��Ͻ� ����
        if dir(module).count('KavMain') != 0 :
            obj = module.KavMain()

        # ������ �ν��Ͻ��� ���ٸ� ���� �ε��� ����� ���
        if obj == None :
            # �ε� ���
            del sys.modules[kmd_name] 
            del module

        return obj # ������ �ν��Ͻ� ����           
            
#---------------------------------------------------------------------
# TEST
#---------------------------------------------------------------------
def cb(list_vir) :
    for vir in list_vir :
        print vir

# ���� Ŭ����
kav = Engine() 
kav.SetPlugings('plugins') # �÷����� ���� ����

print '----------------------------'
# ���� �ν��Ͻ� ����1
kav1 = kav.CreateInstance()
if kav1 == None :
    print 'Error : KICOM Anti-Virus Engine CreateInstance1'
else :
    print kav1

# ���� �ν��Ͻ� ����2
kav2 = kav.CreateInstance()
if kav2 == None :
    print 'Error : KICOM Anti-Virus Engine CreateInstance2'
else :
    print kav2

print '----------------------------'
print kav1.init()
print kav2.init()
print '----------------------------'
s = kav1.getinfo()
for i in s :
    print i['title']
print '----------------------------'
kav1.listvirus(cb)
print '----------------------------'
print kav1.scan('dummy.txt')
print kav1.scan('eicar.txt')
print kav1.scan('kavcore.py')
print '----------------------------'
kav1.uninit()
kav2.uninit()
