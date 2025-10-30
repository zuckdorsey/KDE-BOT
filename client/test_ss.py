#!/usr/bin/env python3
"""
Test which screenshot method works on your system
Run: python test_screenshot.py
"""

import os
import subprocess
import tempfile
import platform


def test_method(name, command, env=None):
    """Test a screenshot method"""
    print(f"\n{'=' * 60}")
    print(f"Testing: {name}")
    print(f"Command: {command}")
    print(f"{'=' * 60}")

    try:
        # Create temp file
        temp_file = os.path.join(tempfile.gettempdir(), f'test_{name.replace(" ", "_")}.png')

        # Replace OUTPUT placeholder
        cmd = command.replace('OUTPUT', temp_file).split()

        # Set environment
        if env is None:
            env = os.environ.copy()
            if 'DISPLAY' not in env:
                env['DISPLAY'] = ':0'

        print(f"Running: {' '.join(cmd)}")

        # Run command
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            timeout=10,
            check=False
        )

        # Check result
        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            size = os.path.getsize(temp_file)
            print(f"✅ SUCCESS - File size: {size} bytes")
            os.remove(temp_file)
            return True
        else:
            print(f"❌ FAILED - Return code: {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.decode()}")
            return False

    except FileNotFoundError:
        print(f"❌ NOT INSTALLED - Command not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT - Command took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False


def main():
    print('\n' + '=' * 60)
    print('🔍 Screenshot Method Tester for Arch Linux')
    print('=' * 60)

    # System info
    print(f"\n📊 System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Display: {os.environ.get('DISPLAY', '(not set)')}")
    print(f"   Session: {os.environ.get('XDG_SESSION_TYPE', '(unknown)')}")
    print(f"   User: {os.environ.get('USER', '(unknown)')}")

    # Test methods
    methods = [
        ('scrot', 'scrot OUTPUT'),
        ('maim', 'maim OUTPUT'),
        ('ImageMagick import', 'import -window root OUTPUT'),
        ('gnome-screenshot', 'gnome-screenshot -f OUTPUT'),
        ('spectacle', 'spectacle -b -n -o OUTPUT'),
        ('grim (Wayland)', 'grim OUTPUT'),
    ]

    working = []

    for name, command in methods:
        if test_method(name, command):
            working.append(name)

    # Summary
    print('\n' + '=' * 60)
    print(f'📋 SUMMARY: {len(working)}/{len(methods)} methods working')
    print('=' * 60)

    if working:
        print(f"\n✅ Working methods:")
        for i, method in enumerate(working, 1):
            print(f"   {i}. {method}")
        print(f"\n💡 Recommended: Use {working[0]}")
    else:
        print("\n❌ No screenshot methods work!")
        print("\n🔧 SOLUTIONS:")
        print("   1. Install scrot:")
        print("      sudo pacman -S scrot")
        print("\n   2. Check DISPLAY variable:")
        print(f"      Current: {os.environ.get('DISPLAY', '(not set)')}")
        print("      Should be: :0 or :1")
        print("\n   3. If using Wayland:")
        print("      sudo pacman -S grim")
        print("\n   4. Check X11 permissions:")
        print("      xhost +local:")

    print('\n' + '=' * 60)


if __name__ == '__main__':
    main()