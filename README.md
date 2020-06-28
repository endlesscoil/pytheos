
Pytheos is a Python library designed to allow easy interaction with devices in the HEOS audio ecosystem.  HEOS is 
supported on specific Denon and Marantz products.

##### Features
* Network discovery via SSDP
* Get current Now Playing status
* Control of all HEOS devices - play, pause, mute, volume, and so on.
* Browse music sources and containers
* Queue & Playlists - creation, modification
* Group management
* HEOS Event support
* .. and everything else as defined in the HEOS CLI Protocol Specification

##### Device Support
This is a partial list of supported devices - I suspect most, if not all, HEOS devices will work fine.
 
###### Confirmed
* Marantz PM7000N (1.562.230)


##### Installation

###### Via PyPI
This library is distributed via PyPI for normal usage and can be installed with the command below. 
<pre>pip install pytheos</pre>

###### Developers
If you wish to do development work on Pytheos you can clone the repository and set up your development environment
with the following commands.
```
git clone https://github.com/endlesscoil/pytheos.git
python setup.py develop
```

##### Example Usage
###### Discovery
HEOS responds to multicast packets on your local network and you can use the pytheos.discovery module 
to broadcast and detect responses from HEOS devices on your network.
```python
import pytheos.discovery

services = pytheos.discovery.discover()

if services:
    print("Discovered these HEOS services:")
    for svc in services:
        print(f'- {svc}')

else:
    print("No HEOS services detected!")
```
Output:
```
- <Pytheos(server=10.10.0.7, port=1255)>
```

###### Direct Connection and Making an API Call
It's also possible to connect directly to a known IP address and port.

After connection you can make use of the API interface to start controlling your device.
```python
import pytheos

with pytheos.connect(('10.10.0.7', 1255)) as svc:
    players = svc.api.player.get_players()
    for p in players:
        print(f'- {p}')
```
Output:
```
- Player(name='Marantz PM7000N', player_id=12345678, group_id=None, model='Marantz PM7000N', version='1.562.230', network=<Network.Wifi: 'wifi'>, ip='10.10.0.7', lineout=<Lineout.NoLineout: 0>, control=None, serial='SN0987654321')
```

###### Subscribing to Events
HEOS connections also support registering for asynchronous events.  These events are triggered in response to a variety
of commands and state changes in the HEOS device itself and allow monitoring and tracking status for your own purposes.

```python
import time

import pytheos
from pytheos.types import HEOSEvent

def _on_now_playing_changed(event: HEOSEvent):
    print(f'Now Playing Changed Event: {event}')

def _on_player_state_changed(event: HEOSEvent):
    print(f'Player State Changed Event: {event}')


with pytheos.connect(('10.10.0.7', 1255)) as svc:
    svc.subscribe('event/player_state_changed', _on_player_state_changed)
    svc.subscribe('event/player_now_playing_changed', _on_now_playing_changed)

    print("Okay, go play something on your stereo - Ctrl+C to stop!")
    try:
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        print('Exiting..')
```
Output:
```
Okay, go play something on your stereo - Ctrl+C to stop!
Player State Changed Event: {"heos": {"command": "event/player_state_changed", "message": "pid=12345678&state=play"}}
Now Playing Changed Event: {"heos": {"command": "event/player_now_playing_changed", "message": "pid=12345678"}}
Player State Changed Event: {"heos": {"command": "event/player_state_changed", "message": "pid=12345678&state=pause"}}
Exiting..
```
