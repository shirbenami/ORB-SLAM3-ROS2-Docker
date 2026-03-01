#!/usr/bin/env python3
import sys
import re

def extract_block(block: str):
    """
    Parse one ROS2 'ros2 topic echo' YAML-like block (single message),
    and return (t, tx, ty, tz, qx, qy, qz, qw) or None if missing.
    Works for PoseStamped-style output:
      header:
        stamp:
          sec: ...
          nanosec: ...
      pose:
        position:
          x: ...
          y: ...
          z: ...
        orientation:
          x: ...
          y: ...
          z: ...
          w: ...
    Also works if pose is nested differently (best-effort).
    """
    def find_float(pattern):
        m = re.search(pattern, block)
        return float(m.group(1)) if m else None

    # timestamp (header.stamp)
    sec = find_float(r"^\s*sec:\s*([-\d\.eE]+)\s*$")
    nsec = find_float(r"^\s*nanosec:\s*([-\d\.eE]+)\s*$")
    if sec is None or nsec is None:
        return None
    t = sec + nsec * 1e-9

    # position: take the FIRST occurrence under a "position:" section if possible,
    # otherwise fallback to first x/y/z triplet we find after the word "position:"
    pos_idx = block.find("position:")
    if pos_idx == -1:
        return None
    pos_part = block[pos_idx:]

    tx = find_float(r"^\s*x:\s*([-\d\.eE]+)\s*$")
    # The regex above finds first x anywhere; we want within pos_part:
    def find_float_in(text, pattern):
        m = re.search(pattern, text, flags=re.MULTILINE)
        return float(m.group(1)) if m else None

    tx = find_float_in(pos_part, r"^\s*x:\s*([-\d\.eE]+)\s*$")
    ty = find_float_in(pos_part, r"^\s*y:\s*([-\d\.eE]+)\s*$")
    tz = find_float_in(pos_part, r"^\s*z:\s*([-\d\.eE]+)\s*$")

    # orientation: similarly
    ori_idx = block.find("orientation:")
    if ori_idx == -1:
        return None
    ori_part = block[ori_idx:]

    qx = find_float_in(ori_part, r"^\s*x:\s*([-\d\.eE]+)\s*$")
    qy = find_float_in(ori_part, r"^\s*y:\s*([-\d\.eE]+)\s*$")
    qz = find_float_in(ori_part, r"^\s*z:\s*([-\d\.eE]+)\s*$")
    qw = find_float_in(ori_part, r"^\s*w:\s*([-\d\.eE]+)\s*$")

    if None in (tx, ty, tz, qx, qy, qz, qw):
        return None

    return (t, tx, ty, tz, qx, qy, qz, qw)


def convert(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    # split by ROS2 echo separator
    blocks = [b.strip() for b in text.split('---') if b.strip()]

    n_written = 0
    with open(output_path, "w", encoding="utf-8") as out:
        for b in blocks:
            res = extract_block(b)
            if res is None:
                continue
            t, tx, ty, tz, qx, qy, qz, qw = res
            out.write(f"{t:.9f} {tx} {ty} {tz} {qx} {qy} {qz} {qw}\n")
            n_written += 1

    print(f"Wrote {n_written} poses to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 ros2_echo_to_tum.py <input.txt> <output.tum>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
