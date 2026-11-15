import sys,unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from http_retry import request_with_retry
class RetryTests(unittest.TestCase):
    def test_rate_limit_waits_then_resumes(self):
        limited=Mock(status_code=429,headers={'Retry-After':'8.017'});ok=Mock(status_code=200)
        call=Mock(side_effect=[limited,ok]);sleep=Mock()
        self.assertIs(request_with_retry(call,sleep=sleep),ok);sleep.assert_called_once_with(8.017)
    def test_auth_failure_is_not_retried(self):
        denied=Mock(status_code=401);call=Mock(return_value=denied);sleep=Mock()
        self.assertIs(request_with_retry(call,sleep=sleep),denied);self.assertEqual(call.call_count,1);sleep.assert_not_called()
    def test_repeated_failure_is_bounded(self):
        fail=Mock(status_code=503,headers={});call=Mock(return_value=fail);sleep=Mock()
        self.assertIs(request_with_retry(call,attempts=3,sleep=sleep),fail);self.assertEqual(call.call_count,3)
if __name__=='__main__':unittest.main()
