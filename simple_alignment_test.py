#!/usr/bin/env python3
"""
Simple test to check exact alignment
"""
def test_simple_alignment():
    # Simulate what should happen
    prefix = "  10:06:17 | ENGAGED      | "
    text = "This is a long line that should wrap properly and the continuation should align with the start of this text"

    print("Expected alignment:")
    print(f"{prefix}{text[:30]}...")
    print(f"{' ' * len(prefix)}{text[30:60]}...")
    print(f"{' ' * len(prefix)}{text[60:90]}...")
    print()

    # Now test our textwrap
    import textwrap
    available_width = 80 - len(prefix)  # Assuming 80 char terminal
    wrapped_lines = textwrap.wrap(text, width=available_width)

    print("Our textwrap result:")
    print(f"{prefix}{wrapped_lines[0]}")
    for line in wrapped_lines[1:]:
        print(f"{' ' * len(prefix)}{line}")

if __name__ == "__main__":
    test_simple_alignment()
