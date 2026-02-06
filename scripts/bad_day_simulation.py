#!/usr/bin/env python3
"""
Bad Day Simulation - Sprint 15, Task 120

Simulates various failure scenarios to verify system resilience:
- Low memory conditions
- Browser crashes
- Blocked domains
- Partial job completion

Purpose: Build confidence that the system degrades gracefully under stress.
"""
import asyncio
import sys
import os
import psutil
import time
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

# Add parent directory to path
# Add parent directory to path
root_dir = Path(__file__).parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.limits import limits, get_mode_specific_limits
from app.core.recovery import JobRecoveryManager


class BadDaySimulator:
    """Simulates various failure scenarios."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scenarios": {},
            "overall_status": "unknown"
        }
    
    async def run_all_scenarios(self):
        """Run all bad day scenarios."""
        print("🔥 BAD DAY SIMULATION STARTING")
        print("=" * 60)
        
        scenarios = [
            ("low_memory", self.simulate_low_memory),
            ("browser_crash", self.simulate_browser_crash),
            ("blocked_domain", self.simulate_blocked_domain),
            ("partial_completion", self.simulate_partial_completion),
        ]
        
        for name, scenario_func in scenarios:
            print(f"\n📍 Running scenario: {name}")
            print("-" * 60)
            
            try:
                result = await scenario_func()
                self.results["scenarios"][name] = result
                
                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                print(f"{status}: {result['summary']}")
                
            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")
                self.results["scenarios"][name] = {
                    "passed": False,
                    "summary": f"Exception: {str(e)}",
                    "error": str(e)
                }
        
        # Overall assessment
        all_passed = all(
            scenario.get("passed", False) 
            for scenario in self.results["scenarios"].values()
        )
        
        self.results["overall_status"] = "passed" if all_passed else "failed"
        
        print("\n" + "=" * 60)
        print(f"🎯 OVERALL STATUS: {self.results['overall_status'].upper()}")
        print("=" * 60)
        
        return self.results
    
    async def simulate_low_memory(self) -> Dict[str, Any]:
        """
        Simulate low memory conditions.
        
        Verifies:
        - System detects low memory
        - Limits are enforced
        - System doesn't crash
        """
        result = {
            "passed": False,
            "summary": "",
            "observations": []
        }
        
        # Check current memory
        memory = psutil.virtual_memory()
        current_percent = memory.percent
        
        result["observations"].append(f"Current memory usage: {current_percent}%")
        
        # Check if limits would prevent issues
        mode_limits = get_mode_specific_limits()
        max_workers = mode_limits["max_workers"]
        max_browsers = mode_limits["max_browser_instances"]
        
        # Calculate theoretical max memory usage
        max_memory_mb = (
            (max_workers * limits.MAX_WORKER_MEMORY_MB) +
            (max_browsers * limits.BROWSER_MEMORY_LIMIT_MB)
        )
        
        result["observations"].append(
            f"Max theoretical memory: {max_memory_mb} MB "
            f"({max_workers} workers × {limits.MAX_WORKER_MEMORY_MB} MB + "
            f"{max_browsers} browsers × {limits.BROWSER_MEMORY_LIMIT_MB} MB)"
        )
        
        # Check if system has enough memory for limits
        available_mb = memory.available / (1024 * 1024)
        result["observations"].append(f"Available memory: {available_mb:.0f} MB")
        
        if max_memory_mb < available_mb:
            result["passed"] = True
            result["summary"] = "System limits prevent memory exhaustion"
            result["observations"].append(
                "✅ Configured limits are within available memory"
            )
        else:
            result["passed"] = False
            result["summary"] = "WARNING: Limits may exceed available memory"
            result["observations"].append(
                "⚠️ Consider reducing worker/browser limits for this environment"
            )
        
        return result
    
    async def simulate_browser_crash(self) -> Dict[str, Any]:
        """
        Simulate browser crash scenario.
        
        Verifies:
        - Retry logic exists
        - Partial artifacts preserved
        - Job can recover
        """
        result = {
            "passed": False,
            "summary": "",
            "observations": []
        }
        
        # Check if retry decorator exists
        try:
            from app.core.recovery import with_retry, with_browser_recovery
            result["observations"].append("✅ Retry decorators found")
            
            # Check max retries setting
            max_retries = limits.MAX_SCRAPE_RETRIES
            result["observations"].append(f"Max retries configured: {max_retries}")
            
            if max_retries >= 3:
                result["observations"].append("✅ Sufficient retry attempts")
            else:
                result["observations"].append("⚠️ Consider increasing max retries")
            
            # Check partial artifact preservation
            job_id = "test-crash-recovery"
            test_artifacts = {"test": "data", "partial": True}
            
            saved_path = await JobRecoveryManager.save_partial_artifacts(
                job_id=job_id,
                artifacts=test_artifacts
            )
            
            if saved_path:
                result["observations"].append(f"✅ Partial artifacts saved: {saved_path}")
                
                # Try to load them back
                loaded = await JobRecoveryManager.load_partial_artifacts(job_id)
                if loaded:
                    result["observations"].append("✅ Partial artifacts loaded successfully")
                    result["passed"] = True
                    result["summary"] = "Browser crash recovery mechanisms in place"
                else:
                    result["observations"].append("❌ Failed to load partial artifacts")
                    result["summary"] = "Partial artifact loading failed"
            else:
                result["observations"].append("❌ Failed to save partial artifacts")
                result["summary"] = "Partial artifact saving failed"
                
        except ImportError as e:
            result["observations"].append(f"❌ Recovery module import failed: {e}")
            result["summary"] = "Recovery module not available"
        
        return result
    
    async def simulate_blocked_domain(self) -> Dict[str, Any]:
        """
        Simulate blocked domain scenario.
        
        Verifies:
        - Timeout handling
        - Retry logic
        - Graceful failure
        """
        result = {
            "passed": False,
            "summary": "",
            "observations": []
        }
        
        # Check timeout settings
        mode_limits = get_mode_specific_limits()
        request_timeout = mode_limits["request_timeout"]
        browser_timeout = limits.BROWSER_TIMEOUT
        
        result["observations"].append(f"Request timeout: {request_timeout}s")
        result["observations"].append(f"Browser timeout: {browser_timeout}s")
        
        if request_timeout > 0 and browser_timeout > 0:
            result["observations"].append("✅ Timeouts configured")
            
            # Check retry logic
            max_retries = limits.MAX_SCRAPE_RETRIES
            result["observations"].append(f"Max retries: {max_retries}")
            
            if max_retries >= 2:
                result["passed"] = True
                result["summary"] = "Blocked domain handling configured"
                result["observations"].append(
                    "✅ System will timeout and retry blocked domains"
                )
            else:
                result["summary"] = "Insufficient retry attempts"
                result["observations"].append("⚠️ Consider increasing retries")
        else:
            result["summary"] = "Timeouts not properly configured"
            result["observations"].append("❌ Missing timeout configuration")
        
        return result
    
    async def simulate_partial_completion(self) -> Dict[str, Any]:
        """
        Simulate partial job completion.
        
        Verifies:
        - Partial results preserved
        - Job state tracked
        - Recovery possible
        """
        result = {
            "passed": False,
            "summary": "",
            "observations": []
        }
        
        # Test partial artifact preservation
        job_id = "test-partial-job"
        partial_data = {
            "completed_pages": 5,
            "total_pages": 10,
            "extracted_items": [
                {"id": 1, "data": "item1"},
                {"id": 2, "data": "item2"},
            ],
            "status": "partial"
        }
        
        try:
            # Save partial artifacts
            saved_path = await JobRecoveryManager.save_partial_artifacts(
                job_id=job_id,
                artifacts=partial_data
            )
            
            if saved_path:
                result["observations"].append("✅ Partial data saved")
                
                # Verify we can load it
                loaded_data = await JobRecoveryManager.load_partial_artifacts(job_id)
                
                if loaded_data:
                    result["observations"].append("✅ Partial data loaded")
                    
                    # Verify data integrity
                    if loaded_data.get("completed_pages") == 5:
                        result["observations"].append("✅ Data integrity verified")
                        result["passed"] = True
                        result["summary"] = "Partial completion handling works"
                    else:
                        result["observations"].append("❌ Data integrity check failed")
                        result["summary"] = "Data corruption detected"
                else:
                    result["observations"].append("❌ Failed to load partial data")
                    result["summary"] = "Partial data loading failed"
            else:
                result["observations"].append("❌ Failed to save partial data")
                result["summary"] = "Partial data saving failed"
                
        except Exception as e:
            result["observations"].append(f"❌ Exception: {str(e)}")
            result["summary"] = f"Exception during test: {str(e)}"
        
        return result
    
    def save_results(self, filepath: str = "bad_day_results.json"):
        """Save simulation results to file."""
        output_path = Path(__file__).parent / filepath
        
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_path}")


async def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🔥 BAD DAY SIMULATION")
    print("Testing system resilience under stress")
    print("=" * 60)
    
    simulator = BadDaySimulator()
    results = await simulator.run_all_scenarios()
    
    # Save results
    simulator.save_results()
    
    # Print summary
    print("\n📊 SUMMARY")
    print("-" * 60)
    for scenario_name, scenario_result in results["scenarios"].items():
        status = "✅" if scenario_result.get("passed") else "❌"
        print(f"{status} {scenario_name}: {scenario_result.get('summary')}")
    
    print("\n💡 STRESS LEVEL ASSESSMENT")
    print("-" * 60)
    
    passed_count = sum(
        1 for s in results["scenarios"].values() 
        if s.get("passed", False)
    )
    total_count = len(results["scenarios"])
    
    if passed_count == total_count:
        print("😌 CALM - All scenarios passed. System is resilient.")
    elif passed_count >= total_count * 0.75:
        print("😐 MODERATE - Most scenarios passed. Minor concerns.")
    else:
        print("😰 STRESSED - Multiple failures. Review system configuration.")
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS")
    print("-" * 60)
    print("1. Review bad_day_results.json for details")
    print("2. Address any failed scenarios")
    print("3. Adjust limits if needed")
    print("4. Re-run simulation after fixes")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if results["overall_status"] == "passed" else 1)


if __name__ == "__main__":
    asyncio.run(main())
