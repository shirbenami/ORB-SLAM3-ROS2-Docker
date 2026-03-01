#!/usr/bin/env python3
import sys, re

def f_in(text, pattern):
    m = re.search(pattern, text, flags=re.MULTILINE)
    return float(m.group(1)) if m else None

def parse_pose_block(block: str):
    # expects:
    # position: x y z
    # orientation: x y z w
    pos_idx = block.find("position:")
    ori_idx = block.find("orientation:")
    if pos_idx == -1 or ori_idx == -1:
        return None

    pos = block[pos_idx:ori_idx]
    ori = block[ori_idx:]

    tx = f_in(pos, r"^\s*x:\s*([-\d\.eE]+)\s*$")
    ty = f_in(pos, r"^\s*y:\s*([-\d\.eE]+)\s*$")
    tz = f_in(pos, r"^\s*z:\s*([-\d\.eE]+)\s*$")

    qx = f_in(ori, r"^\s*x:\s*([-\d\.eE]+)\s*$")
    qy = f_in(ori, r"^\s*y:\s*([-\d\.eE]+)\s*$")
    qz = f_in(ori, r"^\s*z:\s*([-\d\.eE]+)\s*$")
    qw = f_in(ori, r"^\s*w:\s*([-\d\.eE]+)\s*$")

    if None in (tx, ty, tz, qx, qy, qz, qw):
        return None

    return tx, ty, tz, qx, qy, qz, qw

def convert(input_path, output_path, dt):
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    blocks = [b.strip() for b in text.split("---") if b.strip()]

    n_written = 0
    with open(output_path, "w", encoding="utf-8") as out:
        for i, b in enumerate(blocks):
            pose = parse_pose_block(b)
            if pose is None:
                continue
            t = i * dt
            tx, ty, tz, qx, qy, qz, qw = pose
            out.write(f"{t:.9f} {tx} {ty} {tz} {qx} {qy} {qz} {qw}\n")
            n_written += 1

    print(f"Wrote {n_written} poses to {output_path} (dt={dt})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 echo_pose_to_tum.py <input.txt> <output.tum> [dt_seconds]")
        sys.exit(1)

    dt = float(sys.argv[3]) if len(sys.argv) >= 4 else 1.0/30.0  # default 30Hz
    convert(sys.argv[1], sys.argv[2], dt)
