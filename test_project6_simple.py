#!/usr/bin/env python3
"""
Simple test script to test the Project 6 main function
"""

import os
import sys

# Import the function from the bot file
sys.path.append('.')
from bot_serv_GF import main_function_Project_6

def main():
    print("🚀 Testing GF Project 6 Main Function")
    print("=" * 50)
    
    # Check if downloads directory exists
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        print("📁 Created downloads directory")
    
    try:
        print("🌐 Starting Project 6 main function...")
        main_function_Project_6()
        
        print("\n✅ Project 6 main function completed!")
        
        # Check what files were downloaded
        print("\n📁 Downloaded files:")
        for file in os.listdir("downloads"):
            if file.endswith('.csv'):
                file_path = os.path.join("downloads", file)
                file_size = os.path.getsize(file_path)
                print(f"   ✅ {file}: {file_size:,} bytes")
        
        # Check for expected files
        expected_files = ["S1R1A1.csv", "S1R2+A1.csv", "S2R1A1.csv", "S2R2+A1.csv"]
        print(f"\n📊 Expected files check:")
        for expected_file in expected_files:
            file_path = os.path.join("downloads", expected_file)
            if os.path.exists(file_path):
                print(f"   ✅ {expected_file}: Found")
            else:
                print(f"   ❌ {expected_file}: Missing")
        
        print("\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 