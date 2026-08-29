#!/usr/bin/env python3
"""
Minecraft Region Item & Container Locator
Scans modern/legacy Minecraft Anvil (.mca) region files for items, custom names, or container types.
Requires: Python 3.8+ (Zero third-party dependencies).
"""

import argparse
import os
import struct
import sys
import zlib


def extract_coord(data: bytes, tag_name: bytes) -> int | None:
    """Extracts a 4-byte big-endian integer NBT tag by name."""
    pattern = b"\x03" + struct.pack(">H", len(tag_name)) + tag_name
    idx = data.find(pattern)
    if idx != -1:
        val_bytes = data[idx + len(pattern) : idx + len(pattern) + 4]
        if len(val_bytes) == 4:
            return struct.unpack(">i", val_bytes)[0]
    return None


def scan_world(region_dir: str, queries: list[str]) -> None:
    if not os.path.isdir(region_dir):
        print(f"[ERROR] Directory not found: {region_dir}", file=sys.stderr)
        sys.exit(1)

    mca_files = [f for f in os.listdir(region_dir) if f.endswith(".mca")]
    total_files = len(mca_files)

    if total_files == 0:
        print(f"[ERROR] No .mca region files found in: {region_dir}", file=sys.stderr)
        sys.exit(1)

    byte_queries = [q.strip().encode("utf-8") for q in queries if q.strip()]

    print(f"[*] Scanning {total_files} region files in: {region_dir}")
    print(f"[*] Search targets: {queries}\n", flush=True)

    found_count = 0
    total_chunks = 0

    for file_idx, fname in enumerate(mca_files, start=1):
        filepath = os.path.join(region_dir, fname)
        parts = fname.split(".")

        try:
            rx, rz = int(parts[1]), int(parts[2])
        except (IndexError, ValueError):
            continue

        chunks_in_file = 0

        with open(filepath, "rb") as f:
            header = f.read(4096)
            if len(header) < 4096:
                continue

            for i in range(1024):
                offset_bytes = header[i * 4 : i * 4 + 3]
                sector_count = header[i * 4 + 3]
                offset = int.from_bytes(offset_bytes, byteorder="big")

                if offset == 0 or sector_count == 0:
                    continue

                cx = i % 32
                cz = i // 32
                world_chunk_x = rx * 32 + cx
                world_chunk_z = rz * 32 + cz

                f.seek(offset * 4096)
                length_bytes = f.read(4)
                if len(length_bytes) < 4:
                    continue
                length = int.from_bytes(length_bytes, byteorder="big")
                compression_type = f.read(1)
                compressed_data = f.read(length - 1)

                try:
                    if compression_type == b"\x02":
                        chunk_bytes = zlib.decompress(compressed_data)
                    elif compression_type == b"\x01":
                        chunk_bytes = zlib.decompress(compressed_data, 16 + zlib.MAX_WBITS)
                    else:
                        chunk_bytes = compressed_data
                except Exception:
                    continue

                total_chunks += 1
                chunks_in_file += 1

                for query in byte_queries:
                    if query.lower() in chunk_bytes.lower():
                        bx = extract_coord(chunk_bytes, b"x")
                        by = extract_coord(chunk_bytes, b"y")
                        bz = extract_coord(chunk_bytes, b"z")

                        approx_x = world_chunk_x * 16 + 8
                        approx_z = world_chunk_z * 16 + 8

                        print("\n" + "=" * 64, flush=True)
                        print(f"  >>> [MATCH] Target: '{query.decode()}' | Region: {fname}", flush=True)
                        if bx is not None and by is not None and bz is not None:
                            print(f"  >>> EXACT COORDS:  X = {bx}, Y = {by}, Z = {bz}", flush=True)
                        else:
                            print(f"  >>> CHUNK COORDS:  X ~ {approx_x}, Z ~ {approx_z} (Chunk [{world_chunk_x}, {world_chunk_z}])", flush=True)
                        print("=" * 64 + "\n", flush=True)
                        found_count += 1
                        break

        print(f"[{file_idx}/{total_files}] Scanned {fname:<15} | Chunks: {chunks_in_file:<3} | Total: {total_chunks}", flush=True)

    print(f"\n[+] Finished. Scouted {total_chunks} chunks across {total_files} region files.")
    print(f"[+] Total matches located: {found_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Fast standalone Minecraft region scanner to find lost items, chests, and custom containers."
    )
    parser.add_argument(
        "region_dir",
        help="Path to the Minecraft region folder (e.g., path/to/world/region or dimensions/minecraft/overworld/region)",
    )
    parser.add_argument(
        "-q",
        "--query",
        nargs="+",
        required=True,
        help="Item IDs, custom container names, or keywords to search for (e.g., -q netherite_chestplate 'Fireworks' mending)",
    )
    args = parser.parse_args()
    scan_world(args.region_dir, args.query)


if __name__ == "__main__":
    main()