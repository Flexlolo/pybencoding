from typing import Union
from io import BytesIO, BufferedReader, BufferedRWPair

Data 		= Union[BytesIO, BufferedReader, BufferedRWPair]
DataInput 	= Union[str, bytes, Data]
DataDecoded = Union[bytes, int, list, dict]

_INT  		= b'i'
_LIST  		= b'l'
_DICT  		= b'd'
_SEPARATOR 	= b':'
_END 		= b'e'

def _read_until(data: Data, until: bytes) -> bytes:
	buf = bytearray()

	while True:
		byte = data.read(1)

		if not byte:
			raise EOFError(f'EOF when reading until \'{until.decode()}\'')

		if byte == until:
			return buf

		buf += byte

def _decode(data: Data, end: bool = False) -> DataDecoded:
	data_type = data.read(1)

	if not data_type:
		raise EOFError(f'EOF when reading data type at {data.tell()}')

	if data_type == _END:
		if end:
			return None

	elif data_type.isdigit():
		length = int(bytearray(data_type) + _read_until(data, _SEPARATOR))
		string = data.read(length)

		if len(string) != length:
			pos = data.tell() - len(str(length)) - 1 - len(string)
			raise EOFError(f'EOF when reading string at {pos}')

		return string

	elif data_type == _INT:
		return int(_read_until(data, _END))

	elif data_type == _LIST:
		l = list()

		while (item := _decode(data, True)) is not None:
			l.append(item)

		return l

	elif data_type == _DICT:
		d = dict()

		while (key := _decode(data, True)) is not None:
			if (value := _decode(data)) is not None:
				d[key] = value
			else:
				raise EOFError(f'Expected key:value pair but only got key.')

		return d

	raise ValueError(f'Invalid character at {data.tell() - 1}.')

def decode(data: DataInput) -> DataDecoded:
	if isinstance(data, str):
		data = data.encode()
	
	if isinstance(data, bytes):
		data = BytesIO(data)

	return _decode(data)

def _encode(data: DataDecoded, buf: bytearray) -> None:
	if isinstance(data, bytes):
		buf += str(len(data)).encode()
		buf += _SEPARATOR
		buf += data

	elif isinstance(data, int):
		buf += _INT + str(data).encode() + _END

	elif isinstance(data, list):
		buf += _LIST

		for item in data:
			_encode(item, buf)

		buf += _END

	elif isinstance(data, dict):
		buf += _DICT

		for key, value in sorted(data.items()):
			_encode(key, buf)
			_encode(value, buf)

		buf += _END

	else:
		raise ValueError(f'Data type {type(data)} is not supported.')

def encode(data: DataDecoded) -> bytes:
	buf = bytearray()
	_encode(data, buf)

	return bytes(buf)