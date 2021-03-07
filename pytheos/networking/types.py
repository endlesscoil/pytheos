#!/usr/bin/env python
from __future__ import annotations


class SSDPResponse:
    def __init__(self, response):
        self.headers = {}

        fields = response.split('\r\n')
        if len(fields) == 0:
            raise ValueError('Invalid SSDP Response')

        self.protocol, self.response_code, self.response = fields[0].split(' ')
        for f in fields[1:]:
            split_values = f.split(':')

            field_name = split_values[0]
            field_value = ':'.join(split_values[1:]).strip()
            if field_name == '':
                continue

            self.headers[field_name] = field_value

        self.location = self.headers.get('LOCATION')

    def __repr__(self):
        return f"<SSDPResponse(location={self.location})>"
