# Syscoin Address Converter

A simple utility for converting between legacy Syscoin P2PKH address format (Base58) and SegWit v0 P2WPKH Bech32 Syscoin address format.

**Supported Conversions:**
*   Legacy P2PKH (starts with 'S') <---> SegWit v0 P2WPKH (starts with 'sys1q')

**Unsupported Conversions:**
*   Conversion involving legacy P2SH addresses (starting with 'T') is **not supported** due to the ambiguity in determining the original SegWit script type from the P2SH hash.
*   This tool **does not** support conversion to or from Taproot (SegWit v1 / P2TR) addresses (starting with 'sys1p'). It will raise an error if a Taproot address is provided.

This tool helps bridge the gap created by the removal of the `convertaddress` RPC call in Syscoin Core, primarily for systems needing to handle both legacy P2PKH and standard SegWit v0 P2WPKH addresses.

## Installation

Make sure you have Python 3.7+ installed. Then, install the required dependency:

```bash
pip install -r requirements.txt 
# (Installs the 'base58' library)
```

The tool also includes a local copy of the standard Bech32 reference implementation (`bech32_ref.py`), slightly modified for correct case-insensitive decoding, which is used internally.

## Usage

### Command-Line Interface (CLI)

The simplest way to use the converter is via the command line:

```bash
python converter.py <SYSCOIN_LEGACY_P2PKH_OR_SEGWIT_V0_P2WPKH_ADDRESS>
```

**Examples:**

```bash
# Convert Legacy P2PKH ('S') to Segwit v0 P2WPKH ('sys1q')
python converter.py SPd281HLz89nvKZ1js6eeefD3YsjcP78AX
# Output: sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sja

# Convert Segwit v0 P2WPKH ('sys1q') to Legacy P2PKH ('S')
python converter.py sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sja
# Output: SPd281HLz89nvKZ1js6eeefD3YsjcP78AX

# Attempting Taproot ('sys1p') conversion (will produce an error)
python converter.py sys1p2mnq5hr45h2zd7zvz8487zmedufrccp69ql2077q77le47hdhumq89cf5t
# Output (stderr): Error: Unsupported SegWit version (1): Taproot (v1) or future versions cannot be converted.

# Attempting P2SH-Segwit ('3') conversion (will produce an error)
python converter.py 38KSVy4NcgF8L6da8DeWxc8kwWxPkB55zw
# Output (stderr): Error: Invalid Base58 prefix: Expected 63, got 5
```

If an invalid or unsupported address is provided, an error message will be printed to stderr.

### As a Python Module

You can also import the conversion function into your Python code:

```python
from converter import convert_syscoin_address, InvalidAddressError

# Legacy P2PKH to Segwit v0 P2WPKH
legacy_p2pkh = 'SPd281HLz89nvKZ1js6eeefD3YsjcP78AX'
try:
    segwit_p2wpkh = convert_syscoin_address(legacy_p2pkh)
    print(f"Legacy {legacy_p2pkh} -> Segwit {segwit_p2wpkh}")
except InvalidAddressError as e:
    print(f"Error converting {legacy_p2pkh}: {e}")

# Segwit v0 P2WPKH to Legacy P2PKH
segwit_p2wpkh = 'sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sja'
try:
    legacy_p2pkh = convert_syscoin_address(segwit_p2wpkh)
    print(f"Segwit {segwit_p2wpkh} -> Legacy {legacy_p2pkh}")
except InvalidAddressError as e:
    print(f"Error converting {segwit_p2wpkh}: {e}")

# Attempt Taproot Conversion (will raise InvalidAddressError)
taproot_address = 'sys1p2mnq5hr45h2zd7zvz8487zmedufrccp69ql2077q77le47hdhumq89cf5t'
try:
    convert_syscoin_address(taproot_address)
except InvalidAddressError as e:
    print(f"Error converting {taproot_address}: {e}")

# Attempt P2SH Conversion (will raise InvalidAddressError)
legacy_p2sh = '38KSVy4NcgF8L6da8DeWxc8kwWxPkB55zw'
try:
    convert_syscoin_address(legacy_p2sh)
except InvalidAddressError as e:
    print(f"Error converting {legacy_p2sh}: {e}")

```

## Testing

Run tests to validate functionality:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## Details

This tool uses the `base58` library for Base58Check decoding/encoding and includes a local, slightly modified version of the standard Python Bech32 reference implementation (`bech32_ref.py`) for Bech32/Bech32m handling.

It uses the following Syscoin mainnet parameters:
*   Legacy P2PKH Prefix: `63` (Addresses usually start with 'S')
*   Legacy P2SH Prefix: `5` (Addresses usually start with 'T', **conversion not supported**)
*   Bech32 HRP: `sys`
    *   SegWit v0 addresses (P2WPKH) start with `sys1q`.
    *   SegWit v1 addresses (Taproot/P2TR) start with `sys1p` (**conversion not supported**).

## Contributions

Feel free to fork, open issues, or submit pull requests!

## License

MIT

