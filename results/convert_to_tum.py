import sys
import re

def convert(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    out = open(output_file, 'w')

    timestamp = None
    tx = ty = tz = None
    qx = qy = qz = qw = None

    for line in lines:
        line = line.strip()

        if line.startswith("sec:"):
            sec = float(line.split(":")[1].strip())
        if line.startswith("nanosec:"):
            nsec = float(line.split(":")[1].strip())
            timestamp = sec + nsec * 1e-9

        if "position:" in line:
            continue
        if line.startswith("x:") and tx is None:
            tx = float(line.split(":")[1])
        elif line.startswith("y:") and ty is None:
            ty = float(line.split(":")[1])
        elif line.startswith("z:") and tz is None:
            tz = float(line.split(":")[1])

        if "orientation:" in line:
            continue
        if line.startswith("x:") and tx is not None and qx is None:
            qx = float(line.split(":")[1])
        elif line.startswith("y:") and ty is not None and qy is None:
            qy = float(line.split(":")[1])
        elif line.startswith("z:") and tz is not None and qz is None:
            qz = float(line.split(":")[1])
        elif line.startswith("w:"):
            qw = float(line.split(":")[1])

        if all(v is not None for v in [timestamp, tx, ty, tz, qx, qy, qz, qw]):
            out.write(f"{timestamp} {tx} {ty} {tz} {qx} {qy} {qz} {qw}\n")
            tx = ty = tz = None
            qx = qy = qz = qw = None

    out.close()

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
