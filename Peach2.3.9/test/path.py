'''
Test cases for Path/Stop functionality
'''

import unittest
import utils

def suite():
    suite = unittest.TestSuite()
    suite.addTest(OrdinaryPathTest())
    suite.addTest(PathWithChangeStateTest())
    suite.addTest(PathWithStopTest())
    return suite

class OrdinaryPathTest(utils.PeachTcpTestCase):
    
    def runTest(self):
        self.peachUtils.RunPeachXml("path1.xml")
        ret = self.peachUtils.GetListenerData()
        assert ret == 'First Second ', 'path1.xml failed, instead got [%s]' % repr(ret)
 
 
class PathWithChangeStateTest(utils.PeachTcpTestCase):
    
    def runTest(self):
        self.peachUtils.RunPeachXml("path2.xml")
        ret = self.peachUtils.GetListenerData()
        assert ret == 'First Second Third ', 'path2.xml failed, instead got [%s]' % repr(ret)
 
 
 
class PathWithStopTest(utils.PeachTcpTestCase):
    '''
    Actually this is not a proper test as it needs to check 
    if raises an exception when peach receives a Stop signal or not
    but this seems impossible due to Peach's error friendly nature ;) 
    '''
    def runTest(self):
        self.peachUtils.RunPeachXml("path3.xml")
        ret = self.peachUtils.GetListenerData()
        assert ret == 'First Second ', 'path3.xml failed, instead got [%s]' % repr(ret)
 
if __name__ == "__main__":
    unittest.main()

#end
