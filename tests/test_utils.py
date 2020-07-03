#!/usr/bin/env python
from __future__ import annotations

import unittest

from pytheos import utils
from pytheos.utils import CHARACTER_REPLACE_MAP


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
        self.assertEqual(utils.build_command_string("group", "command"), "heos://group/command\n")
        self.assertEqual(utils.build_command_string("group", "command", arg1="hello", other_arg="world", stop=True),
                         "heos://group/command?arg1=hello&other_arg=world&stop=True\n")

        # Confirm replacement characters are working correctly
        input_str = ''
        output_str = ''
        for invalid_char, replacement_char in CHARACTER_REPLACE_MAP.items():
            input_str += invalid_char
            output_str += replacement_char

        self.assertEqual(utils.build_command_string("group", "command", test=input_str),
                         f"heos://group/command?test={output_str}\n")

    def test_parse_var_string(self):
        self.assertEqual(utils.parse_var_string('pid=12345678&un=someone'), {'pid': '12345678', 'un': 'someone'})
        self.assertEqual(utils.parse_var_string('signed_in&un=username'), {'signed_in': 'signed_in', 'un': 'username'})


if __name__ == '__main__':
    unittest.main()
