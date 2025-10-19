#!/usr/bin/env python3

import sys

try:
    import xerxes
    from xerxes.cli import app
    from xerxes.agent.core import Agent
    from xerxes.tools.registry import get_registry

    print("✓ Package imported successfully")
    print(f"✓ xerxes module found at: {xerxes.__file__}")
    print("✓ CLI app available")
    print("✓ Agent class available")
    print("✓ Tool registry available")

    registry = get_registry()
    all_tools = registry.get_all_tools()
    print(f"✓ {len(all_tools)} tools registered")

    print("\n✅ All smoke tests passed!")
    sys.exit(0)

except Exception as e:
    print(f"\n❌ Smoke test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
