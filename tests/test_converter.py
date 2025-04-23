import unittest
from converter import convert_syscoin_address, InvalidAddressError
from bech32_ref import encode as bech32_encode

class TestSyscoinAddressConverter(unittest.TestCase):

    # --- Valid Conversions (Legacy P2PKH <-> Segwit v0 P2WPKH) ---

    # Test Pair 1 (Node verified)
    def test_legacy_p2pkh_to_segwit_p2wpkh_1(self):
        legacy_p2pkh = 'SPd281HLz89nvKZ1js6eeefD3YsjcP78AX'
        segwit_expected = 'sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sja'
        segwit_actual = convert_syscoin_address(legacy_p2pkh)
        self.assertEqual(segwit_actual, segwit_expected)

    def test_segwit_p2wpkh_to_legacy_p2pkh_1(self):
        segwit_p2wpkh = 'sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sja'
        legacy_expected = 'SPd281HLz89nvKZ1js6eeefD3YsjcP78AX'
        legacy_actual = convert_syscoin_address(segwit_p2wpkh)
        self.assertEqual(legacy_actual, legacy_expected)

    # Test Pair 2 (Node verified)
    def test_legacy_p2pkh_to_segwit_p2wpkh_2(self):
        legacy_p2pkh = 'SdUvmXY1J1FmyAELaf3oituhYWZbFwoods'
        segwit_expected = 'sys1qkxfsw46x4weycst8swwl6ge0aszsdwcs78zy6z'
        segwit_actual = convert_syscoin_address(legacy_p2pkh)
        self.assertEqual(segwit_actual, segwit_expected)

    def test_segwit_p2wpkh_to_legacy_p2pkh_2(self):
        segwit_p2wpkh = 'sys1qkxfsw46x4weycst8swwl6ge0aszsdwcs78zy6z'
        legacy_expected = 'SdUvmXY1J1FmyAELaf3oituhYWZbFwoods'
        legacy_actual = convert_syscoin_address(segwit_p2wpkh)
        self.assertEqual(legacy_actual, legacy_expected)

    # --- Invalid / Unsupported Inputs ---

    def test_taproot_address_throws_error(self):
        # Use node-generated Taproot address
        taproot_address = 'sys1p2mnq5hr45h2zd7zvz8487zmedufrccp69ql2077q77le47hdhumq89cf5t'
        with self.assertRaisesRegex(InvalidAddressError, "Unsupported SegWit version \\(1\\)"):
            convert_syscoin_address(taproot_address)

    def test_invalid_checksum_throws_error(self):
        # Use node-generated address with changed checksum
        invalid_legacy = 'SPd281HLz89nvKZ1js6eeefD3YsjcP78AY' # Changed X -> Y
        invalid_bech32 = 'sys1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6ah9sjx' # Changed a -> x

        with self.assertRaisesRegex(InvalidAddressError, "Invalid address: Not valid Base58"):
            convert_syscoin_address(invalid_legacy)
        with self.assertRaisesRegex(InvalidAddressError, "Invalid address: Not valid Base58"):
             convert_syscoin_address(invalid_bech32)

    def test_invalid_format_throws_error(self):
        invalid_format = 'invalidaddressstring'
        with self.assertRaisesRegex(InvalidAddressError, "Invalid address: Not valid Base58"):
            convert_syscoin_address(invalid_format)

    def test_incorrect_hrp_throws_error(self):
        # Use node-generated segwit address structure with wrong HRP
        bitcoin_bech32 = 'bc1qrxy3qhgfzeer9pf9egh4zh3qcn82j9s6tr57ax' # checksum recalculated for bc
        with self.assertRaisesRegex(InvalidAddressError, "Invalid address: Not valid Base58"):
            convert_syscoin_address(bitcoin_bech32)

    def test_incorrect_base58_prefix_throws_error(self):
        # Use a known Bitcoin address (prefix 0)
        bitcoin_legacy = '1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH'
        with self.assertRaisesRegex(InvalidAddressError, "Invalid Base58 prefix"):
            convert_syscoin_address(bitcoin_legacy)

    def test_invalid_segwit_program_length(self):
        hrp = 'sys'
        witver = 0
        witprog_invalid_len = bytes([i % 256 for i in range(21)])
        # Expect encode to fail and return None
        encoded_addr = bech32_encode(hrp, witver, witprog_invalid_len)
        self.assertIsNone(encoded_addr, "bech32_ref.encode should return None for invalid program length")
        # Expect main function to fail early on None input
        with self.assertRaisesRegex(InvalidAddressError, "Address must be a non-empty string"):
            convert_syscoin_address(encoded_addr)

    def test_bech32_case_insensitive_decode(self):
        segwit_mixed_case_correct = 'sYs1qRxY3qHgfZeEr9Pf9eGh4zH3qCn82j9s6Ah9sJa' # Only case differs from sys1qr...
        legacy_expected = 'SPd281HLz89nvKZ1js6eeefD3YsjcP78AX'
        # Use the correctly mixed case address
        legacy_actual = convert_syscoin_address(segwit_mixed_case_correct)
        self.assertEqual(legacy_actual, legacy_expected)

if __name__ == '__main__':
    unittest.main()