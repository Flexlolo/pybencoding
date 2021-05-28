# pybencoding
Minimal and fast implementation of bencoding in python

## Usage
```
from bencoding import encode, decode

with open(file, 'rb') as f:
	torrent = decode(f)

torrent[b'announce'] = b'new url'

with open(file, 'wb') as f:
	f.write(encode(torrent))
```