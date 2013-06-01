# -*- coding:utf-8 -*-
# Made by Kei Choi(hanul93@gmail.com)

import unittest
import shutil
import os
import kavcore

class Test_Dummy_Cure(unittest.TestCase):
    def test_kav_dummy(self):
        self.kav = kavcore.Engine() # ���� Ŭ����
        self.kav.SetPlugings('plugins') # �÷����� ���� ����

        # ���� �ν��Ͻ� ����1
        self.kav1 = self.kav.CreateInstance()
        self.assertTrue(self.kav1 != None)

        # ���� �ʱ�ȭ
        ret = self.kav1.init()
        self.assertTrue(ret != False)

        # �Ǽ��ڵ� �˻�
        self.kav1.scan('eicar.txt')
        ret = self.kav1.get_result()
        self.assertTrue(ret['Files'] == 1)
        self.assertTrue(ret['Infected_files'] == 1)

        # ���� ����
        self.kav1.uninit()


if __name__ == '__main__':
    unittest.main()
