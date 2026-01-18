
import sys
import os
sys.path.append(os.getcwd())

print("🔍 Verifying Phase 4 (BattleService Move)...")

try:
    # 1. Check File Location
    if not os.path.exists("src/Core/BattleService.py"):
        raise Exception("src/Core/BattleService.py not found!")
    print("✅ File exists at src/Core/BattleService.py")

    # 2. Check Import from Core
    from src.Core import BattleService, init_service, get_service
    print("✅ Successfully imported BattleService from src.Core")

    # 3. Check Service Instantiation (dry run)
    service = init_service()
    print("✅ Service initialized via Core init_service")
    
    assert isinstance(service, BattleService)
    print("✅ Service instance is of correct type")

    # 4. Check internal imports (if they failed, init would likely fail)
    # Check if config is accessible
    print(f"✅ Service Prompt Mapping accessible: {len(service.roles['dream'].prompt) > 0}")

    service.cleanup()
    print("✅ Service cleanup OK")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n🎉 Phase 4 Verification PASSED")
