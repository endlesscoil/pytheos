![Python package](https://github.com/endlesscoil/pytheos/workflows/Python%20package/badge.svg)

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
* Marantz PM7000N (1.583.201)

##### Installation

###### Via PyPI
TBD

###### Developers
If you wish to do development work on Pytheos you can clone the repository and set up your development environment
with the following commands.
```
git clone https://github.com/endlesscoil/pytheos.git
python setup.py develop
```

##### Example Usage
See the [Examples](https://github.com/endlesscoil/pytheos/tree/master/examples) directory.
