# Copyright (c) 2017, 2020 Pieter Wuille
# ... (rest of license header) ...

"""Reference implementation for Bech32/Bech32m and segwit addresses."""

from enum import Enum

class Encoding(Enum):
    """Enumeration type to list the various supported encodings."""
    BECH32 = 1
    BECH32M = 2

CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

BECH32M_CONST = 0x2bc830a3

def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    generator = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for value in values:
        top = chk >> 25
        chk = (chk & 0x1ffffff) << 5 ^ value
        for i in range(5):
            chk ^= generator[i] if ((top >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    """Expand the HRP into values for checksum computation."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_verify_checksum(hrp, data):
    """Verify a checksum given HRP and converted data characters."""
    const = bech32_polymod(bech32_hrp_expand(hrp) + data)
    if const == 1:
        return Encoding.BECH32
    if const == BECH32M_CONST:
        return Encoding.BECH32M
    return None

def bech32_create_checksum(hrp, data, spec):
    """Compute the checksum values given HRP and data."""
    values = bech32_hrp_expand(hrp) + data
    const = BECH32M_CONST if spec == Encoding.BECH32M else 1
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def _bech32_encode_impl(hrp, data, spec):
    """Compute a Bech32 string given HRP and data values."""
    combined = data + bech32_create_checksum(hrp, data, spec)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def _bech32_decode_impl(bech):
    """Validate a Bech32/Bech32m string, and determine HRP and data."""
    # Check for invalid characters (ASCII 33-126)
    if ((any(ord(x) < 33 or ord(x) > 126 for x in bech))):
        # REMOVED explicit mixed-case check: or (bech.lower() != bech and bech.upper() != bech)
        return (None, None, None)
    bech = bech.lower() # Convert to lowercase for processing
    pos = bech.rfind('1')
    if pos < 1 or pos + 7 > len(bech) or len(bech) > 90:
        return (None, None, None)
    if not all(x in CHARSET for x in bech[pos+1:]):
        return (None, None, None)
    hrp = bech[:pos]
    data = [CHARSET.find(x) for x in bech[pos+1:]]
    spec = bech32_verify_checksum(hrp, data) # Checksum verification
    if spec is None:
        return (None, None, None)
    return (hrp, data[:-6], spec)

def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret

def decode(hrp, addr):
    """Decode a segwit address."""
    hrpgot, data, spec = _bech32_decode_impl(addr)
    if hrpgot != hrp:
        return (None, None)
    decoded = convertbits(data[1:], 5, 8, False)
    if decoded is None or len(decoded) < 2 or len(decoded) > 40:
        return (None, None)
    if data[0] > 16:
        return (None, None)
    if data[0] == 0 and len(decoded) != 20 and len(decoded) != 32:
        return (None, None)
    # BIP350: Check spec vs witness version
    if data[0] == 0 and spec != Encoding.BECH32 or data[0] != 0 and spec != Encoding.BECH32M:
        return (None, None)
    return (data[0], decoded)

def encode(hrp, witver, witprog):
    """Encode a segwit address."""
    # BIP350: Use Bech32m for v1+ addresses
    spec = Encoding.BECH32 if witver == 0 else Encoding.BECH32M
    data_5bit = convertbits(witprog, 8, 5, True)
    if data_5bit is None:
        return None # Error during conversion
    ret = _bech32_encode_impl(hrp, [witver] + data_5bit, spec)
    # Double-check that the result is valid (decode sanity check)
    if decode(hrp, ret) == (None, None):
        return None
    return ret 