#!/usr/bin/env python
import unittest

from pytheos import utils


class TestUtils(unittest.TestCase):
    def test_extract_ip(self):
        self.assertEqual(utils.extract_host('http://127.0.0.1'), '127.0.0.1')
        self.assertEqual(utils.extract_host('http://127.0.0.1/'), '127.0.0.1')
        self.assertEqual(utils.extract_host('http://127.0.0.1/testing'), '127.0.0.1')
        self.assertEqual(utils.extract_host('http://127.0.0.1:1234'), '127.0.0.1')
        self.assertEqual(utils.extract_host('http://127.0.0.1:1234/testing'), '127.0.0.1')
        self.assertEqual(utils.extract_host('https://127.0.0.1'), '127.0.0.1')

        self.assertIsNone(utils.extract_host('hxxp://127.0.0.1'))

    def test_build_command_string(self):
        self.assertEqual(utils.build_command_string("system", "heart_beat"), "heos://system/heart_beat\n")
        self.assertEqual(utils.build_command_string("group", "command", arg1="hello", other_arg="world", stop=True), "heos://group/command?arg1=hello&other_arg=world&stop=True\n")
        # FIXME: This needs more

    def test_parse_var_string(self):
        self.assertEqual(utils.parse_var_string('pid=12345678&un=someone'), {'pid': '12345678', 'un': 'someone'})


if __name__ == '__main__':
    unittest.main()
