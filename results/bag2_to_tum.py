#!/usr/bin/env python3
import sys
from pathlib import Path

from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize
from rosbags.typesys import get_typestore

def write_tum_from_topic(bag_dir: Path, topic: str, out_path: Path):
    typestore = get_typestore('ros2_humble')  # מספיק לרוב המקרים (Pose/PoseStamped)
    n = 0

    with Reader(str(bag_dir)) as reader, out_path.open('w') as out:
        # build map: connection -> msgtype
        conn_by_topic = {c.topic: c for c in reader.connections}
        if topic not in conn_by_topic:
            topics = sorted(set(c.topic for c in reader.connections))
            raise SystemExit(f"Topic {topic} not found in bag. Available:\n" + "\n".join(topics))

        for conn, t_ns, raw in reader.messages():
            if conn.topic != topic:
                continue

            msg = deserialize_cdr(raw, conn.msgtype, typestore)

            # Bag timestamp (ns) -> seconds
            t = t_ns * 1e-9

            # Support PoseStamped and Pose
            if hasattr(msg, 'pose'):
                pose = msg.pose
            else:
                pose = msg

            p = pose.position
            q = pose.orientation

            out.write(f"{t:.9f} {p.x} {p.y} {p.z} {q.x} {q.y} {q.z} {q.w}\n")
            n += 1

    print(f"Wrote {n} poses from {topic} -> {out_path}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 bag2_to_tum.py <bag_dir> <topic> <out_tum.txt>")
        sys.exit(1)

    bag_dir = Path(sys.argv[1])
    topic = sys.argv[2]
    out_path = Path(sys.argv[3])

    write_tum_from_topic(bag_dir, topic, out_path)

if __name__ == "__main__":
    main()
