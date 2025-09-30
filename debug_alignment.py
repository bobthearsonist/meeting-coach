#!/usr/bin/env python3
"""
Debug alignment issues
"""
def debug_alignment():
    # Let's manually check what the alignment should be
    alert_indicator = "  "  # 2 chars
    timestamp = "10:06:17"  # 8 chars
    pipe1 = " | "  # 3 chars
    state = "engaged"  # variable length, but padded to 12
    state_padded = f"{state.upper():<12}"  # 12 chars
    pipe2 = " | "  # 3 chars

    prefix = f"{alert_indicator}{timestamp}{pipe1}{state_padded}{pipe2}"
    print(f"Prefix length: {len(prefix)}")
    print(f"Prefix: '{prefix}'")
    print(f"Visual: {prefix}TEXT_STARTS_HERE")
    print(f"Spaces: {' ' * len(prefix)}^")
    print()

    # Test with different state lengths
    states = ["calm", "engaged", "elevated", "intense", "overwhelmed"]
    for state in states:
        state_padded = f"{state.upper():<12}"
        prefix = f"{alert_indicator}{timestamp}{pipe1}{state_padded}{pipe2}"
        print(f"{state:>10}: '{prefix}' (len={len(prefix)})")

if __name__ == "__main__":
    debug_alignment()
