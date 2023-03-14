from bsp.json import JSON


MAX_SAFE_INTERGR = 2 ** 53 - 1


def encode(*data) -> bytearray:
    buf = bytearray()

    for payload in data:
        _type = type(payload)
        __type = -1

        if payload == None:
            __type = 0  # null
            payload = bytearray()

        elif _type == str:  # string
            __type = 1
            payload = bytearray(payload, "utf8")

        elif _type == int or _type == float:
            if _type == int and payload > MAX_SAFE_INTERGR:
                __type = 3  # bigint
            else:
                __type = 2  # number
            payload = bytearray(str(payload), "utf8")

        elif _type == bool:  # boolean
            __type = 4
            payload = bytearray([int(payload)])

        elif _type == bytearray:
            __type = 6  # binary

        else:
            try:
                __type = 5  # object
                payload = bytearray(JSON.stringify(payload), "utf8")
            except:
                raise Exception("unsupported payload type %s" % str(_type))

        head = [__type]
        length = len(payload)

        if length <= 255:
            head.append(1)
            head.append(length)

        else:
            binlen = -1

            if length <= 65535:
                head.append(2)
                binlen = 16
            else:
                head.append(3)
                binlen = 64

            binstr = "{0:{fill}{len}b}".format(length, fill='0', len=binlen)

            for i in range(0, binlen, 8):
                j = i + 8
                head.append(int(binstr[i:j], 2))

        buf = buf + bytearray(head) + payload

    return buf


def parsePayloadInfo(buf: bytearray):
    if len(buf) < 3:
        return None  # head frame

    _type = buf[0]
    lenType = buf[1]

    if _type > 6 or lenType > 3:
        return False  # malformed/unencoded data

    offset = [0, 3, 4, 10][lenType]
    length = -1

    if len(buf) < offset:
        return None  # head frame

    if lenType == 1:
        length = buf[2]

    else:
        headEnd = lenType == 2 and 4 or 10
        binstr = ""

        for i in range(2, headEnd):
            binstr = binstr + "{0:{fill}8b}".format(buf[i], fill='0')

        length = int(binstr, 2)

    return [_type, offset, length]


def isHeaderTemp(temp: list) -> bool:
    return len(temp) == 3 and temp[0] == None and temp[1] == None and type(temp[2]) == bytearray


def fillTemp(buf: bytearray, temp: list) -> None:
    if isHeaderTemp(temp):
        buf = temp[2] + buf

    info = parsePayloadInfo(buf)

    if info == False:
        return  # malformed/unencoded data

    elif info == None:
        temp[0] = temp[1] = None
        temp[2] = buf

    else:
        _type = info[0]
        offset = info[1]
        length = info[2]

        if offset != 0:
            temp[0] = _type
            temp[1] = length
            temp[2] = buf[offset:]


def decodeSegment(buf: bytearray, temp: list) -> iter:
    if len(temp) != 3:
        raise Exception("argument 'temp' must be a list with 3 elements")

    # put the buffer into the temp
    elif temp[2] == None or isHeaderTemp(temp):
        fillTemp(buf, temp)

    else:
        temp[2] = temp[2] + buf

    while temp[2] != None and len(temp[2]) >= temp[1]:
        _type = temp[0]
        length = temp[1]
        buf = temp[2]
        payload = buf[0:length]
        buf = buf[length:]

        if _type == 0:  # null
            yield None

        elif _type == 1:  # string
            yield payload.decode("utf8")

        elif _type == 2:  # number
            _str = payload.decode("utf8")
            yield "." in _str and float(_str) or int(_str)

        elif _type == 3:  # bigint
            yield int(payload.decode("utf8"))

        elif _type == 4:  # boolean
            yield bool(payload[0])

        elif _type == 5:  # object
            yield JSON.parse(payload.decode("utf8"))

        elif _type == 6:  # binary
            yield payload

        else:
            raise Exception(
                "unknown payload type 0x{0:{fill}2X}".format(buf[i], fill='0'))

        if len(buf) > 0:
            fillTemp(buf, temp)

        else:  # clear
            temp[0] = None
            temp[1] = None
            temp[2] = None


def decode(buf: bytearray, temp=None):
    if type(temp) == list:
        return decodeSegment(buf, temp)
    else:
        return next(decodeSegment(buf, [None] * 3))
