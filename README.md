In this assignment, you will learn about hash functions: how they are constructed, how they behave, and how weaknesses can be demonstrated empirically. You will implement a Merkle–Damgård hash function using our precode, evaluate its properties, and compare your implementation to SHA-256 as a baseline.

We use an Alice–Bob scenario throughout: Alice uses hashing to commit to messages, protect integrity, and build data structures (Merkle trees). An attacker (Eve) tries to exploit weaknesses such as collisions, weak diffusion (poor avalanche), and structural issues (e.g., length extension in a toy setting).

To complete this assigmnent you will need to

Implement the required functions in precode;
run experiments and report your measurements; and
answer specific questions given in each task.
Precode 
Download: A3_Precode_MD_hash (Canvas folder)
Precode filename: a3_precode_merkle_damgard.py
How to run: python3 a3_precode_merkle_damgard.py --help
Important: You must start from the provided template and complete the TODO sections. Do not replace the template with an unrelated implementation.

Learning Objectives
Understand how block-based hash functions are constructed (compression + iteration).
Implement Merkle–Damgård padding and iterative hashing.
Measure avalanche effect and collision resistance empirically.
Understand and demonstrate length extension (toy setting).
Build and verify Merkle tree inclusion proofs.
System Overview
You will implement and evaluate a toy hash based on the Merkle–Damgård construction. Your work includes:

Low-level primitives (bit/byte operations used by the hash core)
Compression function (the block mixing step)
Merkle–Damgård hashing (padding + iteration + digest)
Evaluation experiments (avalanche, collision search, performance)
Constructions using hashing (length extension in a toy misuse setting, Merkle trees)
Implementation
You must implement the required functions in the provided template and run the experiments using the provided CLI. You may use Python’s standard library and the allowed dependencies already referenced by the template.

System Requirements
To get a passing grade on this assignment, your submission must adhere to the following requirements:

You must use the provided template and complete the TODO sections.
You must run the required experiments and report measured results (numbers) in the PDF.
You must answer all questions in the given order (do not merge or reorder questions).
You must perform at least 200 trials for the avalanche experiment.
You must run at least 5 independent trials per chosen truncation size for collision search.
You must implement Merkle tree root computation, inclusion proof generation, and verification.
You must compare results to SHA-256 (avalanche, truncated collisions, performance).
Report
You are required to hand in a report describing your work. The report must include answers to the questions below, in the same order as the tasks.

Tasks
Task 1: Bit and Byte Operations (Warm-up)
Goal: Implement safe and correct low-level primitives used by the hash core.

u32(x)                 # force integer into 32-bit range
rotl32(x, n)           # rotate-left (32-bit)
rotr32(x, n)           # rotate-right (32-bit)
xor_bytes(a, b)        # XOR two byte strings (equal length)
hamming_distance(a,b)  # bit-wise Hamming distance between byte strings
flip_one_random_bit(data)  # mutate exactly one random bit
Questions:

What does it mean to mask a value to 32 bits in Python, and why is this necessary?
Explain the difference between bit shifts and bit rotations. Why are rotations common in hash functions?
Task 2: Implement the Compression Function
Implement the toy compression function exactly as specified in the template. The function mixes an 8-word internal state with a 64-byte message block using modular addition, XOR, and rotation.

compress(state_words, block_bytes) -> new_state_words
Questions:

What role does the compression function play in an iterative hash construction?
Why do hash designs combine addition, XOR, and rotation instead of using a single operation?
Task 3: Build the Hash Function (Merkle–Damgård)
Implement the full toy hash function using Merkle–Damgård construction: padding, block processing, and digest output.

md_pad(message_bytes) -> padded_bytes
toyhash(message_bytes) -> 32-byte digest
toyhash_hex(message_bytes) -> hex string
Questions:

Why is padding required in block-based hash functions?
Why is the message length included in the padding?
Explain the difference between preimage resistance and collision resistance.
Task 4: Avalanche Effect Experiment
Measure how many output bits change when exactly one input bit is flipped. Run at least 200 trials and report the mean and standard deviation. Repeat the experiment using SHA-256 for comparison.

avalanche_experiment(hash_fn, trials=200)
Questions:

What avalanche behavior would you expect from a well-designed hash function?
Compare the avalanche results of your toy hash with SHA-256. What do you observe?
Task 5: Collision Search on Truncated Digests
Truncate the hash output to a small number of bits (suggested: 16, 20, 24) and empirically search for collisions. For each k_bits, run at least 5 independent trials and report average attempts until collision. Compare your results to the expected birthday bound behavior.

find_truncated_collision(hash_fn, k_bits)
Questions:

Explain the birthday paradox in the context of hash functions.
Do your experimental results match the expected order of growth? Why or why not?
Task 6: Length Extension Attack (Toy Setting)
Demonstrate a length extension attack against the toy hash when it is misused as: toyhash(secret || message).

toyhash_stateful(message)
toyhash_extend(digest, orig_len, extra)
Questions:

Explain what a length extension attack is, in your own words.
Show how Eve can forge a valid hash for an extended message without knowing the secret.
What is the standard real-world fix for this vulnerability?
Task 7: Merkle Tree Hashing
Build a Merkle tree using your toy hash function. Compute the root, generate an inclusion proof, and verify the proof.

merkle_root(leaves, hash_fn)
merkle_proof(leaves, index, hash_fn)
merkle_verify(leaf, index, proof, root, hash_fn)
Questions:

Why are Merkle trees useful for protecting the integrity of large datasets?
What information must an inclusion proof contain, and why?
Task 8: Comparison with SHA-256
Compare your toy hash with SHA-256 in terms of: (1) avalanche effect, (2) collision resistance (truncated), and (3) performance (hashes per second).

Questions:

Which metrics show the largest difference between the toy hash and SHA-256?
Based on your results, where is your toy hash weakest, and why?