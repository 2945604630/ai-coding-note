"""Three real core scenarios. Missing accepted Docker means SKIP, never host fallback."""
import os
from pathlib import Path
import shutil
import unittest
from web_lab.sandbox_runtime import DockerRuntime


@unittest.skipUnless(shutil.which('docker'),'Docker 未安装；禁止使用主机 Python 冒充沙箱')
class RealSandbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime=DockerRuntime(Path(os.environ.get('AIC_SANDBOX_TEST_DATA_DIR','data/aic_demo')))
        if not cls.runtime.status()['ready']:
            raise unittest.SkipTest('需要先完成 sandbox_setup build/accept')

    def test_correct_program_matches_reference(self):
        r=self.runtime.execute('def solve(n):\n    return n*(n+1)//2\n',3)
        self.assertTrue(r['executed'] and r['cleaned'])
        self.assertEqual(r['status'],'completed');self.assertEqual(r['stdout'],'6\n')

    def test_wrong_program_has_verifiable_difference(self):
        r=self.runtime.execute('def solve(n):\n    return n*(n-1)//2\n',3)
        self.assertTrue(r['executed'] and r['cleaned'])
        self.assertEqual(r['status'],'completed');self.assertEqual(r['stdout'],'3\n')
        self.assertNotEqual(r['stdout'],'6\n')

    def test_infinite_loop_is_terminated(self):
        r=self.runtime.execute('def solve(n):\n    while True:\n        pass\n',3)
        self.assertTrue(r['executed'] and r['cleaned'])
        self.assertEqual(r['status'],'timeout')


if __name__=='__main__':unittest.main()
