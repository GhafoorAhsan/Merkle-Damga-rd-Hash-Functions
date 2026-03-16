#!/usr/bin/env python3
"""
a3_precode_merkle_damgard.py — PRECODE TEMPLATE (Bachelor Assignment)

A3: Merkle–Damgård Hash Functions — Design, Implementation, and Evaluation

This template provides:
- function signatures + TODO sections students must complete
- a fixed toy compression function spec (constants + schedule)
- CLI to run required experiments
- basic self-tests for utilities + padding shape

Students must implement TODO sections. The toy hash is for learning only.
Do NOT use this in production systems.

Submission tip (recommended workflow):
- Copy this file to: src/a3-<username>.py
- Fill in the TODOs without changing the provided structure.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
import time
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple, Optional, Dict, Any

# ============================================================
# Configuration (toy Merkle–Damgård hash)
# ============================================================

BLOCK_SIZE = 64            # bytes
DIGEST_SIZE = 32           # bytes (256-bit)
STATE_WORDS = 8            # 8 x 32-bit words

# Fixed IV (course-specific; toy)
IV = [
    0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344,
    0xA4093822, 0x299F31D0, 0x082EFA98, 0xEC4E6C89,
]

# Round constants (toy)
RC = [
    0x9E3779B9, 0x7F4A7C15, 0xF39CC060, 0x106AA070,
    0xC2B2AE35, 0x27D4EB2F, 0x165667B1, 0xD3A2646C,
    0xFD7046C5, 0xB55A4F09, 0xA5A35625, 0x3C6EF372,
]

# Rotation schedule (toy)
R = [5, 11, 17, 23, 7, 13, 19, 29]

# ============================================================
# Task 1: Bit and Byte Operations (Warm-up) (TODO)
# ============================================================

def u32(x: int) -> int:
    """Force x into unsigned 32-bit range."""
    return x & 0xFFFFFFFF 

def rotl32(x: int, n: int) -> int:
    """Rotate-left 32-bit."""
    x = u32(x) # x is treated as unsigned 32 bit value
    n %= 32 # n is in range of 0 to 31
    # shift bits left, combine, takes the bits that fell off the left side and put them back on the right, trim  to 32 bits
    return u32((x << n) | (x >> (32 -n)))

def rotr32(x: int, n: int) -> int:
    """Rotate-right 32-bit."""
    x = u32(x) # x is treated as unsigned 32 bit value
    n %= 32 # n is in range of 0 to 31 
    # shift bits right, combine, takes the bits that fell off the right side and put them back on the left, trim to 32 bits
    return u32((x >> n) | (x << (32 - n)))

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte strings."""
    if (len(a) != len(b)): # check if the lengths are equal 
        raise ValueError("required equal length")
    # XOR each pair of bytes from a and b, return as bytes 
    # x ^ y computes XOR for each pair.
    # zip(a, b) pairs corresponding bytes
    return bytes(x ^ y for x, y in zip(a, b)) 

def hamming_distance(a: bytes, b: bytes) -> int:
    """Bitwise Hamming distance between byte strings."""
    if (len(a) != len(b)): # check if the length are equal 
        raise ValueError("required equal length")
    # Count how many bits differ between two equal-length byte strings.
    # XOR each pair of bytes.
    # In the XOR result, every 1 means a bit was different.
    # .bit_count() counts how many 1s there are.
    # sum(...) adds them up across all bytes.
    return sum((x ^ y).bit_count() for x, y in zip(a, b))

def flip_one_random_bit(data: bytes) -> bytes:
    """Return a copy of data with exactly one random bit flipped."""
    if len(data) == 0: # check if data is empty
        raise ValueError("data must be non-empty")
    
    out = bytearray(data) # mutable copy of data 

    # os.urandom(4) gives 4 random bytes
    # int.from_bytes(..., "little") turns them into an integer
    # % len(out) makes sure the result is a valid index into the byte array
    byte_index = int.from_bytes(os.urandom(4), "little") % len(out) 

    # chooses a random bit inside that byte
    # converted to integer
    # % 8 gives a number from 0 to 7
    bit_index = int.from_bytes(os.urandom(1), "little") % 8

    # Flips that bit from the original byte value:
        # 1 << bit_index makes a bit mask with exactly one 1
        # ^= means XOR in place
        # XOR with 1 flips the bit:
            # 0 becomes 1, 1 becomes 0
    out[byte_index] ^= (1 << bit_index)

    # Converts back to regular bytes.
    return bytes(out) 

# ============================================================
# Encoding helpers (provided)
# ============================================================

def bytes_to_words_le(block: bytes) -> List[int]:
    """64 bytes -> 16 little-endian u32 words."""
    if len(block) != BLOCK_SIZE:
        raise ValueError("block must be 64 bytes")
    return list(struct.unpack("<16I", block))

def words_to_bytes_le(words8: Sequence[int]) -> bytes:
    """8 u32 words -> 32 bytes."""
    if len(words8) != STATE_WORDS:
        raise ValueError("need 8 words")
    return struct.pack("<8I", *[u32(w) for w in words8])

def digest_to_state_words_le(digest: bytes) -> List[int]:
    """32-byte digest -> 8 little-endian u32 words."""
    if len(digest) != DIGEST_SIZE:
        raise ValueError("digest must be 32 bytes")
    return list(struct.unpack("<8I", digest))

# ============================================================
# Task 2: Implement the Compression Function (TODO)
# ============================================================

def compress(state: Sequence[int], block: bytes) -> List[int]:
    """
    Toy compression function spec (must implement exactly):

    Input:
        state: 8 x u32
        block: 64 bytes -> 16 x u32 message words m[0..15]

    Working vars:
        v0..v7 = state words (u32)

    For round i in 0..11:
        t0 = u32(v0 + m[(i*5 + 0) % 16] + RC[i])
        v4 = u32(v4 ^ rotl32(t0, R[(i + 0) % 8]))
        v0 = u32(v0 + v4)

        t1 = u32(v1 + m[(i*5 + 1) % 16] + RC[i])
        v5 = u32(v5 ^ rotl32(t1, R[(i + 1) % 8]))
        v1 = u32(v1 + v5)

        t2 = u32(v2 + m[(i*5 + 2) % 16] + RC[i])
        v6 = u32(v6 ^ rotl32(t2, R[(i + 2) % 8]))
        v2 = u32(v2 + v6)

        t3 = u32(v3 + m[(i*5 + 3) % 16] + RC[i])
        v7 = u32(v7 ^ rotl32(t3, R[(i + 3) % 8]))
        v3 = u32(v3 + v7)

        # cross-mix / permutation
        if i % 2 == 0:
            v0, v1, v2, v3 = v1, v2, v3, v0
        else:
            v4, v5, v6, v7 = v6, v7, v4, v5

    Output:
        new_state[j] = u32(state[j] ^ vj ^ v(j+4))
        (i.e., combine old chaining value with mixed vars)

    It takes:
        state: the current internal hash state, sequence of 8 integers 
        block: one 64-byte message block 
    Returns:
        a new 8-word state 
    """

    # Ensure state has exactly 8 words, and block has exactly 64 bytes 
    if len(state) != STATE_WORDS:
        raise ValueError("State must contain 8 words")
    if len(block) != BLOCK_SIZE:
        raise ValueError("Block must be 64 bytes")
    
    # Convert into 16 words --> 1 word = 4 bytes --> 64/4 = 16 
    # m[0] to m[15] are the 16 message words from the block. 
    m = bytes_to_words_le(block)

    # Copy state words into working variables 
    # Takes the 8 state words and puts them into local variables 
    # Easier to update them round by round 
    # u32(w) forces each value into 32-bit range 
    # v0..v7 are the working state values 
    # Original state stays unchanged 
    v0, v1, v2, v3, v4, v5, v6, v7 = [u32(w) for w in state]

    # Main loop of 12 rounds --> the compression runs for 12 rounds
    # Each round mixes current state value, one or more message words, one round constant RC[i] and rotations from R[...]
    for i in range(12):
        # Create a temp value (t0) from current state word (v), one message word and one round constant
        # Change message index every round 
        t0 = u32(v0 + m[(i * 5 + 0) % 16] + RC[i])

        # Rotate t0, XORs into v4 --> v4 is updated using a transformed version of t0 
        v4 = u32(v4 ^ rotl32(t0, R[(i + 0) % 8]))
        
        # Update v0 by adding the new v4 --> v0 and v4 influence each other 
        v0 = u32(v0 + v4)

        # Same patterm (Each lane adds a message word and round constant, rotates, XORs, adds again) for :
            # v1 with v5
            # v2 with v6
            # v3 with v7
        # Each round has 4 parallel mixing lanes:
            # (v0, v4)
            # (v1, v5)
            # (v2, v6)
            # (v3, v7)
        t1 = u32(v1 + m[(i * 5 + 1) % 16] + RC[i])
        v5 = u32(v5 ^rotl32(t1, R[(i + 1) % 8]))
        v1 = u32(v1 + v5)

        t2 = u32(v2 + m[(i * 5 + 2) % 16] + RC[i])
        v6 = u32(v6 ^rotl32(t2, R[(i + 2) % 8]))
        v2 = u32(v2 + v6)

        # End of each round permute part of the state
        # Make values move around so the whole state gets mixed better
        if i % 2 == 0:
            # rotate the first four words left if even 
            v0, v1,v2, v3 = v1, v2, v3, v0 
        else:
            # Rearrange the last four words if odd
            v4, v5, v6, v7 = v6, v7, v4, v5 

    # After 12 rounds --> store the final working variables 
    mixed = [v0, v1, v2, v3, v4, v5, v6, v7]

    # Feed forward design 
    # For each position j, combine:
        # The original input state word state[j]
        # The same position mixed word mixed[j]
        # Another mixed word halfway around the state mixed[(j + 4) % 8]
    # Each output word depends on:
        # Old state
        # Local mixed value 
        # Another mixed value from other half
    return [u32(state[j] ^ mixed[j] ^ mixed[(j + 4) % 8]) for j in range(STATE_WORDS)] 


# ============================================================
# Task 3: Build the Hash Function (Merkle–Damgård) (TODO)
# ============================================================

def md_pad(msg: bytes) -> bytes:
    """
    Merkle–Damgård padding for 64-byte blocks:
    - append 0x80
    - append 0x00 until (len % 64) == 56
    - append 8-byte little-endian bit-length of original message

    Input: 
        msg: the original message as bytes
    Output: 
        The padded message 
    """
    # Message length in bytes 
    # Padding stores in bits --> multiply by 8
    # Keep only the lowest 64 bits 
    # Why:
    #   The length field at the end is exactly 8 bytes = 64 bits
    #   Match the standard stule of MD padding 
    #   Example --> message of 3 bytes long = 3 * 8 = 24 
    bit_len = (len(msg) * 8) & 0xFFFFFFFFFFFFFFFF
    
    # Pad with 0x80 --> adds a single 1 bit followed by seven 0 bits --> Mark where the padding starts 
    pad = b"\x80"
    
    # Compute how many zero bytes are needed 
    # The goal is after adding 0x80 and the zero bytes, the message length should be 56 bytes mod 64 
    # 56 because the final 8 bytes are reserved for the length field and 56 + 8 = 64
    # Do len(msg) + 1 --> because the 0x80 byte has already been added conceptually 
    # Do modulo BLOCK_SIZE because blocks are 64 bytes
    zero_len = (56 - ((len(msg) + 1) % BLOCK_SIZE)) % BLOCK_SIZE
    
    # Append zero bytes --> fill the gap with zeros
    pad += b"\x00" * zero_len
    
    # Append 8-byte little-endian length 
    # Convert bit_len into 8 bytes --> "<" = little-endian, "Q" = unsigned 64-bit integer 
    # bit_len = 24 --> b'\x18\x00\x00\x00\x00\x00\x00\x00' because 24 in hex is 0x18
    pad += struct.pack("<Q", bit_len)
    
    # Return original message plus padding
    # Final result is "original message || 0x80 || zeros || length"
    return msg + pad 

def toyhash(msg: bytes) -> bytes:
    """
    Return 32-byte digest of msg.

    Must:
      - initialize state = IV
      - pad with md_pad
      - iterate compress over each 64-byte block
      - output words_to_bytes_le(state)
    """
    # TODO(Task 3): implement
    raise NotImplementedError

def toyhash_hex(msg: bytes) -> str:
    return toyhash(msg).hex()

# ============================================================
# Task 6: Length Extension Attack (Toy Setting) (TODO)
# ============================================================

@dataclass
class ToyHashState:
    h: List[int]          # internal state (8 x u32)
    total_len: int        # total message length processed so far (bytes)

def toyhash_stateful(msg: bytes) -> Tuple[bytes, ToyHashState]:
    """
    Return (digest, state) after hashing msg.

    This is used ONLY for the length extension task. The returned state should
    contain:
      - internal chaining value (8 x u32)
      - total_len = number of bytes of ORIGINAL (unpadded) message processed
    """
    # TODO(Task 6): implement
    raise NotImplementedError

def toyhash_extend(
    digest: bytes,
    orig_len: int,
    extra: bytes,
    state_override: Optional[ToyHashState] = None
) -> bytes:
    """
    Compute toyhash( orig || pad(orig) || extra ) given:
      - digest = toyhash(orig) (interpreted as internal chaining value)
      - orig_len = len(orig) in bytes (orig contents may be unknown)
      - extra = attacker-chosen extension

    Notes (template conventions):
      - digest is 32 bytes, interpreted as 8 little-endian u32 words.
      - You must reconstruct the "glue padding" that md_pad(orig) would add,
        based only on orig_len.
      - Then continue hashing extra starting from the chaining value implied
        by digest (or from state_override if provided for testing).
    """
    # TODO(Task 6): implement
    raise NotImplementedError

# ============================================================
# Task 7: Merkle Tree Hashing (TODO)
# ============================================================

def merkle_root(leaves: Sequence[bytes], hash_fn: Callable[[bytes], bytes]) -> bytes:
    """
    Compute Merkle root for leaf data.

    Convention (must be consistent across root/proof/verify):
      - leaf hashes: h_i = hash_fn(leaves[i])
      - parent: hash_fn(left_hash || right_hash)
      - if odd number of nodes at a level: duplicate the last node
    """
    # TODO(Task 7): implement
    raise NotImplementedError

def merkle_proof(leaves: Sequence[bytes], index: int, hash_fn: Callable[[bytes], bytes]) -> List[Tuple[bytes, str]]:
    """
    Return inclusion proof as a list of (sibling_hash, direction) where direction is 'L' or 'R':
      - 'L' means sibling is on the Left of the current node
      - 'R' means sibling is on the Right of the current node

    The verifier reconstructs the root by concatenating in the right order:
      - if direction == 'L': parent = hash_fn(sibling || current)
      - if direction == 'R': parent = hash_fn(current || sibling)
    """
    # TODO(Task 7): implement
    raise NotImplementedError

def merkle_verify(
    leaf: bytes,
    index: int,
    proof: Sequence[Tuple[bytes, str]],
    root: bytes,
    hash_fn: Callable[[bytes], bytes]
) -> bool:
    """Verify inclusion proof for leaf under the conventions documented above."""
    # TODO(Task 7): implement
    raise NotImplementedError

# ============================================================
# Experiments (Tasks 4, 5, 8) — provided
# ============================================================

def sha256_bytes(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def truncate_bits(digest: bytes, k_bits: int) -> bytes:
    """Truncate digest to k bits (k <= len(digest)*8)."""
    if k_bits < 1 or k_bits > len(digest) * 8:
        raise ValueError("bad k_bits")
    nbytes = (k_bits + 7) // 8
    out = bytearray(digest[:nbytes])
    extra = (8 - (k_bits % 8)) % 8
    if extra:
        out[-1] &= (0xFF << extra) & 0xFF
    return bytes(out)

def avalanche_experiment(hash_fn: Callable[[bytes], bytes], trials: int = 200, msg_len: int = 64) -> Dict[str, float]:
    total = 0
    total2 = 0
    for _ in range(trials):
        msg = os.urandom(msg_len)
        msg2 = flip_one_random_bit(msg)
        d1 = hash_fn(msg)
        d2 = hash_fn(msg2)
        hd = hamming_distance(d1, d2)
        total += hd
        total2 += hd * hd
    mean = total / trials
    var = (total2 / trials) - (mean * mean)
    std = (var ** 0.5) if var > 0 else 0.0
    return {"trials": float(trials), "mean_bits_changed": mean, "std_bits_changed": std}

def find_truncated_collision(hash_fn: Callable[[bytes], bytes], k_bits: int, max_attempts: int = 500000) -> Dict[str, Any]:
    """
    Single trial collision search on k-bit truncated digests.
    The assignment requires multiple independent trials; the CLI supports that.
    """
    seen: Dict[bytes, bytes] = {}
    for i in range(1, max_attempts + 1):
        msg = os.urandom(32)
        t = truncate_bits(hash_fn(msg), k_bits)
        if t in seen and seen[t] != msg:
            return {"found": True, "attempts": i, "k_bits": k_bits, "m1": seen[t].hex(), "m2": msg.hex(), "trunc": t.hex()}
        seen[t] = msg
    return {"found": False, "attempts": max_attempts, "k_bits": k_bits}

def throughput(hash_fn: Callable[[bytes], bytes], seconds: float = 1.0, msg_len: int = 64) -> float:
    start = time.time()
    count = 0
    while True:
        _ = hash_fn(os.urandom(msg_len))
        count += 1
        if time.time() - start >= seconds:
            break
    return count / seconds

# ============================================================
# Self-tests (basic)
# ============================================================

def self_test() -> None:
    # Task 1 tests
    assert u32(-1) == 0xFFFFFFFF
    assert rotl32(0x12345678, 8) == 0x34567812
    assert rotr32(0x12345678, 8) == 0x78123456
    assert xor_bytes(b"\x00\xFF", b"\x0F\x0F") == b"\x0F\xF0"
    assert hamming_distance(b"\x00", b"\xFF") == 8

    # Task 3 padding shape check (not a test vector)
    m = b"abc"
    p = md_pad(m)
    assert len(p) % 64 == 0
    assert p[:3] == b"abc"
    bitlen = int.from_bytes(p[-8:], "little")
    assert bitlen == len(m) * 8

    # toyhash basic determinism/length checks
    d = toyhash(b"")
    assert isinstance(d, (bytes, bytearray)) and len(d) == 32
    assert toyhash(b"hello") == toyhash(b"hello")

    print("[OK] self_test passed")

# ============================================================
# CLI
# ============================================================

def main() -> None:
    ap = argparse.ArgumentParser(description="A3 Merkle–Damgård Hash Lab — toy hash + experiments")
    ap.add_argument("--self-test", action="store_true", help="run built-in self tests")
    ap.add_argument("--hash", type=str, default=None, help="hash a UTF-8 string with toyhash and sha256")

    ap.add_argument("--avalanche", action="store_true", help="run avalanche experiment for toyhash and sha256")
    ap.add_argument("--avalanche-trials", type=int, default=200, help="number of avalanche trials (>=200 required)")

    ap.add_argument("--collision", type=int, default=None, help="run truncated collision search with k bits (e.g., 16/20/24)")
    ap.add_argument("--collision-trials", type=int, default=5, help="independent collision trials to run (>=5 required)")
    ap.add_argument("--collision-max-attempts", type=int, default=500000, help="max attempts per collision trial")

    ap.add_argument("--throughput", action="store_true", help="measure hashes/sec for toyhash and sha256")
    ap.add_argument("--merkle-demo", action="store_true", help="run a small Merkle tree demo (toyhash)")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if args.hash is not None:
        data = args.hash.encode("utf-8")
        print("toyhash :", toyhash_hex(data))
        print("sha256  :", sha256_bytes(data).hex())
        return

    if args.avalanche:
        trials = args.avalanche_trials
        print("toyhash:", avalanche_experiment(toyhash, trials=trials))
        print("sha256 :", avalanche_experiment(sha256_bytes, trials=trials))
        return

    if args.collision is not None:
        k = args.collision
        n = args.collision_trials
        max_attempts = args.collision_max_attempts

        def run_many(label: str, fn: Callable[[bytes], bytes]) -> None:
            results = []
            for _ in range(n):
                r = find_truncated_collision(fn, k, max_attempts=max_attempts)
                results.append(r)
            attempts = [r["attempts"] for r in results if r.get("found")]
            found_all = all(r.get("found") for r in results)
            avg = (sum(attempts) / len(attempts)) if attempts else float("nan")
            print(f"{label}: trials={n} found_all={found_all} avg_attempts={avg}")
            for i, r in enumerate(results, 1):
                print(f"  trial {i}: {r}")

        run_many("toyhash", toyhash)
        run_many("sha256 ", sha256_bytes)
        return

    if args.throughput:
        print("toyhash hashes/sec:", throughput(toyhash, seconds=1.0))
        print("sha256 hashes/sec :", throughput(sha256_bytes, seconds=1.0))
        return

    if args.merkle_demo:
        leaves = [b"tx1", b"tx2", b"tx3", b"tx4", b"tx5"]
        root = merkle_root(leaves, toyhash)
        proof = merkle_proof(leaves, 2, toyhash)  # tx3
        ok = merkle_verify(leaves[2], 2, proof, root, toyhash)
        print("root :", root.hex())
        print("proof:", [(h.hex(), d) for (h, d) in proof])
        print("verify:", ok)
        return

    ap.print_help()

if __name__ == "__main__":
    main()