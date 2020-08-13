#!/usr/bin/env python
from __future__ import annotations

from pytheos.discovery import SSDPBroadcastMessage

import unittest


DISCOVERY_RESPONSE = "\r\n".join((
    'HTTP/1.1 200 OK',
    'CACHE-CONTROL: max-age=180',
    'EXT:',
    'LOCATION: http://10.1.0.7:60006/upnp/desc/aios_device/aios_device.xml',
    'VERSIONS.UPNP.HEOS.COM: 10,-2098495903,-521045671,363364703,2105748424,105553199,-316033077,1711326982,-170053632,363364703,392989532',
    'NETWORKID.UPNP.HEOS.COM: 001122334455',
    'BOOTID.UPNP.ORG: 123456789',
    'IPCACHE.URL.UPNP.HEOS.COM: /ajax/upnp/get_device_info',
    'SERVER: LINUX UPnP/1.0 Denon-Heos/159889',
    'ST: urn:schemas-denon-com:device:ACT-Denon:1',
    'USN: uuid:11223344-5566-7788-9900-0123456789ab::urn:schemas-denon-com:device:ACT-Denon:1',
    ''
))


class TestDiscovery(unittest.TestCase):
    def test_SSDPBroadcastMessage_construction(self):
        msg = SSDPBroadcastMessage('239.255.255.250',
                                   1900,
                                   "urn:schemas-denon-com:device:ACT-Denon:1",
                                   3)

        self.assertEqual(str(msg), "\r\n".join((
            'M-SEARCH * HTTP/1.1',
            'HOST: 239.255.255.250:1900',
            'MAN: "ssdp:discover"',
            'ST: urn:schemas-denon-com:device:ACT-Denon:1',
            'MX: 3',
            '',
            ''
        )))

    def test_discover(self):
        self.fail('FIXME - Figure out how to mock this.')
        #with patch.object(socket, 'makefile', return_value=io.BytesIO(DISCOVERY_RESPONSE.encode('utf-8'))):
        # with unittest.mock.patch('socket.socket') as mock_socket:
        #     #mock_socket.return_value.fp.readline.return_value = DISCOVERY_RESPONSE.encode('utf-8')
        #     mock_socket.return_value.recv.return_value = DISCOVERY_RESPONSE.encode('utf-8')
        #     # _SSDPResponse = MagicMock(SSDPResponse)
        #     # _SSDPResponse.
        #     with unittest.mock.patch('pytheos.types.SSDPResponse') as mock_response:
        #         mock_response.return_value.fp.readline = unittest.mock.Mock()
        #         discovered = pytheos.discover()
        #         self.assertIsInstance(discovered[0], pytheos.Pytheos)


if __name__== '__main__':
    unittest.main()
