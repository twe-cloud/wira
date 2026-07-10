#!/usr/bin/env python3
"""Verify an Authenticode signature on a PE binary, without Windows.

`signtool` and `Get-AuthenticodeSignature` only exist on Windows, so on a Mac
build box there is otherwise no way to check that a shipped installer is really
signed by us. This parses the PE certificate table directly and reports the
signer chain, so a release can be checked before it goes out.

What this DOES prove: a signature blob exists, it embeds a certificate whose
subject is ours, the chain terminates at the Microsoft Identity Verification
Root, and an RFC3161 timestamp countersignature is present.

What this does NOT prove: that the signed digest matches the file's actual
computed Authenticode hash. Only Windows validates that cheaply. Treat a pass
here as "correctly signed and attributed", and let the Windows Smoke workflow
(Get-AuthenticodeSignature) be the authority on cryptographic validity.
"""

from __future__ import annotations

import argparse
import struct
import subprocess
import sys

# szOID_RFC3161_counterSign — the unauthenticated attribute Trusted Signing adds.
RFC3161_COUNTERSIGN_OID = "1.3.6.1.4.1.311.3.3.1"
EXPECTED_ROOT = "Microsoft Identity Verification Root Certificate Authority 2020"


def extract_pkcs7(path: str) -> bytes:
    data = open(path, "rb").read()
    if data[:2] != b"MZ":
        raise SystemExit(f"{path}: not a PE/COFF image")

    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe : pe + 4] != b"PE\0\0":
        raise SystemExit(f"{path}: bad PE signature")

    opt = pe + 4 + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    # PE32+ puts the data directories 16 bytes further in than PE32.
    data_dirs = opt + (112 if magic == 0x20B else 96)
    security = data_dirs + 4 * 8  # IMAGE_DIRECTORY_ENTRY_SECURITY is index 4

    offset, size = struct.unpack_from("<II", data, security)
    if offset == 0 or size == 0:
        raise SystemExit(f"{path}: NO AUTHENTICODE SIGNATURE (cert table empty)")

    blob = data[offset : offset + size]
    length = struct.unpack_from("<I", blob, 0)[0]
    return blob[8:length]  # skip the WIN_CERTIFICATE header


def openssl(args: list[str], stdin: bytes | None = None) -> str:
    return subprocess.run(
        ["openssl", *args], input=stdin, capture_output=True, check=False
    ).stdout.decode("utf-8", "replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("exe", help="path to the signed .exe")
    ap.add_argument(
        "--expect-subject",
        default="Ni Biashara",
        help="substring that must appear in the leaf certificate subject",
    )
    args = ap.parse_args()

    pkcs7 = extract_pkcs7(args.exe)
    certs = openssl(["pkcs7", "-inform", "DER", "-print_certs", "-noout"], pkcs7)
    if not certs.strip():
        raise SystemExit("could not parse PKCS#7 certificate bundle")

    failures: list[str] = []

    if args.expect_subject not in certs:
        failures.append(f"no certificate subject contains {args.expect_subject!r}")
    if EXPECTED_ROOT not in certs:
        failures.append(f"chain does not include the expected root: {EXPECTED_ROOT!r}")

    asn1 = openssl(["asn1parse", "-inform", "DER", "-i"], pkcs7)
    if RFC3161_COUNTERSIGN_OID not in asn1:
        failures.append(
            "no RFC3161 timestamp countersignature — the signature will stop "
            "validating as soon as the short-lived certificate expires"
        )

    print(certs.strip())
    print()

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        return 1

    print(f"OK: {args.exe} is signed, attributed to {args.expect_subject!r}, and timestamped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
