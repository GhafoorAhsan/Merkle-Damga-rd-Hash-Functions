# INF-2310 Assignment 3 — Merkle–Damgård Hash Functions

## Overview
This submission contains my implementation and evaluation of a toy Merkle–Damgård hash function based on the provided precode template for INF-2310 Assignment 3.

The work includes:

- Low-level bit and byte helper functions
- Toy compression function
- Merkle–Damgård padding and full hash function
- Avalanche experiment
- Truncated collision search
- Toy length extension functionality
- Merkle tree root, proof generation, and proof verification
- Comparison with SHA-256

## Folder Structure
```text
ahgha0019/
├── src/
│   └── a3_ahgha0019.py
├── doc/
│   └── a3_ahgha0019.pdf
└── README.md
```

## Python Version

This code was written and tested with:

- Python 3.10+

## How to Run

Go into the src/ directory and run the script with Python 3.

## Self-Test

Run the built-in self-test to verify that the helper functions, padding, and toy hash behave correctly:

python3 a3_ahgha0019.py --self-test

Expected output:

- [OK] self_test passed

## Hash a Message

To hash a UTF-8 string with both the toy hash and SHA-256:

python3 a3_ahgha0019.py --hash "hello"

## Reproducing the Avalanche Experiment

The assignment requires at least 200 trials. The following command runs the avalanche experiment for both the toy hash and SHA-256:

python3 a3_ahgha0019.py --avalanche --avalanche-trials 200

This prints:

- number of trials
- mean changed bits
- standard deviation

## Reproducing the Collision Experiments

The assignment requires at least 5 independent trials per truncation size.

Run the following commands:

python3 a3_ahgha0019.py --collision 16 --collision-trials 5
python3 a3_ahgha0019.py --collision 20 --collision-trials 5
python3 a3_ahgha0019.py --collision 24 --collision-trials 5

These commands print:

- Whether collisions were found
- Average attempts until collision
- Individual trial results

## Reproducing the Throughput Comparison

To measure hashes per second for the toy hash and SHA-256:

python3 a3_ahgha0019.py --throughput

## Reproducing the Merkle Tree Demo

To compute a small Merkle root, generate an inclusion proof, and verify it:

python3 a3_ahgha0019.py --merkle-demo

This prints:

- Merkle root
- Inclusion proof
- Verification result

## Length Extension Functionality

The code also includes the required functions for the toy length extension task:

- toyhash_stateful(message)
- toyhash_extend(digest, orig_len, extra)

These are implemented in the script as required by the assignment and are discussed in the report.
