import sys
import base58
# Use the reference implementation copied locally
from bech32_ref import encode as bech32_encode, decode as bech32_decode

# Syscoin parameters:
SYSCOIN_P2PKH_PREFIX = 63 # S...
SYSCOIN_P2SH_PREFIX = 5   # T...
SYSCOIN_BECH32_HRP = 'sys'

class InvalidAddressError(ValueError):
    """Custom exception for invalid Syscoin addresses."""
    pass

def convert_syscoin_address(address):
    """Converts a Syscoin address between legacy P2PKH (S...) and SegWit v0 P2WPKH (sys1q...)."""
    if not address or not isinstance(address, str):
        raise InvalidAddressError("Address must be a non-empty string")

    original_address = address

    # --- Try Bech32 Decode using bech32_ref.decode ---
    try:
        # Note: bech32_ref.decode handles case-insensitivity internally
        witver, witprog_8bit = bech32_decode(SYSCOIN_BECH32_HRP, address)
        if witver is not None: # Successfully decoded as Bech32/Bech32m with matching HRP
            prog_bytes = bytes(witprog_8bit)
            prog_len = len(prog_bytes)

            # Check witness version (decode validates 0-16 and spec)
            if witver > 0:
                raise InvalidAddressError(f"Unsupported SegWit version ({witver}): Taproot (v1) or future versions cannot be converted.")

            # Bech32 to Legacy Conversion (witver == 0)
            # decode validates length is 20 or 32 for v0
            if prog_len == 20: # P2WPKH -> P2PKH
                version_byte = bytes([SYSCOIN_P2PKH_PREFIX])
                return base58.b58encode_check(version_byte + prog_bytes).decode('ascii')
            elif prog_len == 32: # P2WSH -> P2SH
                version_byte = bytes([SYSCOIN_P2SH_PREFIX])
                return base58.b58encode_check(version_byte + prog_bytes).decode('ascii')
            else:
                 # Should be unreachable due to decode checks
                 raise InvalidAddressError(f"Internal Error: Invalid SegWit v0 program length after decode: {prog_len} bytes")
        # else: # Decode failed
             # print("DEBUG: Decode failed (witver is None), proceeding to Base58.") # DEBUG

    except InvalidAddressError as e:
        # Re-raise specific errors we created (witver)
        raise e
    except ValueError:
        # Failed Bech32 decoding (checksum, format, HRP mismatch, etc.) -> proceed to Base58
        pass

    # --- If Bech32 decode failed (witver is None OR ValueError was caught), Try Base58 Decode ---
    # The code execution reaches here only if bech32_decode returned (None, None) or raised ValueError
    try:
        decoded_bytes = base58.b58decode_check(original_address)
        prefix = decoded_bytes[0]
        payload = decoded_bytes[1:]
        payload_len = len(payload)

        # --- Legacy P2PKH to Bech32 P2WPKH Conversion --- 
        if prefix == SYSCOIN_P2PKH_PREFIX: # P2PKH -> P2WPKH
            if payload_len == 20:
                encoded = bech32_encode(SYSCOIN_BECH32_HRP, 0, payload)
                if encoded is None:
                    raise InvalidAddressError("Failed to encode P2PKH to Bech32")
                return encoded
            else:
                 raise InvalidAddressError(f"Invalid P2PKH payload length: {payload_len} bytes")
        else:
            raise InvalidAddressError(f"Invalid Base58 prefix: Expected {SYSCOIN_P2PKH_PREFIX}, got {prefix}")

    except InvalidAddressError as e:
         raise e
    except ValueError as base58_decode_error:
         raise InvalidAddressError(f"Invalid address: Not valid Base58 ({base58_decode_error}) or supported Bech32 HRP '{SYSCOIN_BECH32_HRP}'")

def main():
    # --- CLI part moved into main() function ---
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert a Syscoin address between legacy P2PKH (S...) and segwit v0 P2WPKH (sys1q...)."
    )
    parser.add_argument("address", help="The Syscoin address to convert.")

    # Use sys.argv directly for checking length before parsing
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("Error: Too many arguments provided.", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    try:
        converted_address = convert_syscoin_address(args.address)
        print(converted_address)
    except InvalidAddressError as e: # Catch our specific error
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        print(f"Details: {type(e)}", file=sys.stderr)
        sys.exit(1)

# Keep the standard boilerplate to run main() when script is executed directly
if __name__ == "__main__":
    main()
