# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import hashlib  # MD5 �ؽø� ����ϱ� ���� import
import zlib     # ���� �� ������ ���� import
import StringIO # ���� IO�� ���� import
import marshal  # ����ȭ �� ���ڿ��� ���� import
import imp      # ������� �ε��� ���� import
import sys      # ��� ����� ���� import
import types    # Ÿ�� äŷ�� ���� import
import os

#---------------------------------------------------------------------
# load_kmd(fname)
# ��ȣȭ �� ��� ���� ����� kmd ������ ��ȣȭ �ϴ� �Լ�
#---------------------------------------------------------------------
def load_kmd(fname) :
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
        return False, '' # ����

#---------------------------------------------------------------------
# load_set(plugins)
# kmd ����� �ε� ���� ����Ʈ�� �Ѱ��ִ� �Լ�
#---------------------------------------------------------------------
def load_set(plugins) :
    kmd_list = []

    try :
        # kicom.kmd ������ ��ȣȭ
        pathname = plugins + '\\kicom.kmd'
        pathname = os.path.normcase(pathname)
        ret, buf = load_kmd(pathname)

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
        pass
    
    return kmd_list # kmd ���� ����Ʈ ����

#-----------------------------------------------------------------
# import_kmd(kmd_name)
# ��ȣȭ �� ��� ���� ����� kmd ������ import �ϴ� �Լ�
#-----------------------------------------------------------------
def import_kmd(kmd_name, buf) :
    code = marshal.loads(buf[8:]) # ���۸� ������ ������ ����ȭ �� ���ڿ��� ��ȯ
    module = imp.new_module(kmd_name) # ���ο� ��� ����
    exec(code, module.__dict__) # ����ȭ �� ���ڿ��� �������Ͽ� ���� ����
    sys.modules[kmd_name] = module # �������� ��밡���ϰ� ���

    obj = None

    for clsName in dir(module): # �ε��� ��⿡�� KavMain�� �ִ��� �˻�
        if clsName.find('KavMain') == 0 : # KavMain�� �߰ߵǾ����� Ŭ������ �ν��Ͻ� ����
            obj = module.KavMain()

    # ������ �ν��Ͻ��� ���ٸ� ���� �ε��� ����� ���
    if obj == None :
        # �ε� ���
        del sys.modules[kmd_name] 
        del module

    return obj # ������ �ν��Ͻ� ����

#---------------------------------------------------------------------
# Engine Ŭ����
# Ű�޹�� ������ �������̽� Ŭ����
#---------------------------------------------------------------------
class Engine :
    modules = []
    #-----------------------------------------------------------------
    # init(self, plugins)
    # Ű�޹�� ������ �ʱ�ȭ �Ѵ�.
    # ���ڰ� : plugins - ��� ���� ����� �����ϴ� ����
    # ���ϰ� : ���� ���� (True, False)
    #-----------------------------------------------------------------
    def init(self, plugins) :
        ret = False

        try :
            # kmd �ε� �켱���� ����Ʈ�� ���� kmd ���Ͽ��� ����Ʈ Ȯ��
            kmd_list = load_set(plugins) # kicom.kmd ���� �ε�
            if len(kmd_list) == 0 :      # ��� ���� ������ ����
                raise SystemError 

            # kmd �ε� �켱���� ����Ʈ ������ ���� �ε�
            for kmd in kmd_list :
                pathname = plugins + '\\' + kmd
                pathname = os.path.normcase(pathname)
                ret_kmd, buf = load_kmd(pathname)
                if ret_kmd == True :
                    mod = import_kmd(kmd.split('.')[0], buf)
                    # ���� �ε� �Ǿ����� ��� ���� ����Ʈ�� �߰�
                    if mod != None :
                        self.modules.append(mod)

            # �ε��� ����� �ϳ��� ������ ����
            if len(self.modules) == 0 : 
                raise SystemError 

            # ��� ��� ���� ����� init ��� �Լ� ȣ��
            for i in range(len(self.modules)) :
                mod = self.modules[i]
                for api in dir(mod) :
                    if api == 'init' : # init ��� �Լ��� ������
                        ret_init = mod.init() # ȣ��
                        break

            ret = True
        except :
            pass

        return ret

    #-----------------------------------------------------------------
    # uninit(self)
    # Ű�޹�� ������ ����ȭ �Ѵ�.
    #-----------------------------------------------------------------
    def uninit(self) :
        # ��� ���� ����� uninit ��� �Լ� ȣ��
        for i in range(len(self.modules)) :
            mod = self.modules[i]
            for api in dir(mod) :
                if api == 'uninit' :
                    ret_uninit = mod.uninit()
                    break

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

        for i in range(len(self.modules)) :
            mod = self.modules[i]
            for api in dir(mod) :
                if api == 'listvirus' :
                    ret_listvirus = mod.listvirus()

                    # callback �Լ��� �ִٸ� 
                    # callback �Լ� ȣ��
                    if type(cb) is types.FunctionType :
                        cb(ret_listvirus)
                    # callback �Լ��� ���ٸ� 
                    # �Ǽ��ڵ� �̸��� ����Ʈ�� ����
                    else :
                        ret += ret_listvirus

                    break

        # callback �Լ� ������ ������ �Ǽ��ڵ� ����Ʈ�� ����
        if argc == 0 :
            return ret

    #-----------------------------------------------------------------
    # getinfo(self)
    # Ű�޹�� ������ �����ϴ� �Ǽ��ڵ� �̸��� �����Ѵ�.
    #-----------------------------------------------------------------
    def getinfo(self) :
        ret = []

        # ��� ���� ����� getinfo ��� �Լ� ȣ��
        for i in range(len(self.modules)) :
            mod = self.modules[i]
            for api in dir(mod) :
                if api == 'getinfo' :
                    ret_getinfo = mod.getinfo()
                    ret.append(ret_getinfo)
                    break

        return ret

    #-----------------------------------------------------------------
    # scan(self, filename)
    # Ű�޹�� ������ �Ǽ��ڵ带 �����Ѵ�.
    #-----------------------------------------------------------------
    def scan(self, filename) :
        ret = False

        try :
            fp = open(filename, 'rb')
            
            # ��� ���� ����� scan ��� �Լ� ȣ��
            for i in range(len(self.modules)) :
                mod = self.modules[i]
                for api in dir(mod) :
                    if api == 'scan' :
                        ret, vname, id = mod.scan(fp, filename)
                        if ret == True : # �Ǽ��ڵ� �߰��̸� �˻� �ߴ�
                            break
                if ret == True :
                    break

            fp.close()

            return ret, i, vname, id
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
            for api in dir(mod) :
                if api == 'disinfect' :
                    ret_disinfect = mod.disinfect(filename, virusID)
                elif api == 'getinfo' :
                    print mod.getinfo()['title']


        except :
            pass

        return ret_disinfect

#---------------------------------------------------------------------
# TEST
#---------------------------------------------------------------------
kav = Engine()
ret = kav.init('plugins')
if ret == False :
    print 'Error : KICOM Anti-Virus Engine init'
    exit()

kav.listvirus()
kav.getinfo()

ret, modID, vname, id =  kav.scan(sys.argv[1])
if ret == True :
    print vname
    print kav.disinfect(sys.argv[1], modID, id)


kav.uninit()