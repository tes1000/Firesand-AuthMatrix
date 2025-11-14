# PySide6 LGPL Compliance Guide

This document explains how Firesand Auth Matrix complies with PySide6's LGPL-3.0 license for commercial use.

## Overview

PySide6 (Qt for Python) is licensed under LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only. This project uses it under the LGPL-3.0 terms, which allows commercial use with specific requirements.

## LGPL-3.0 Key Requirements

### ✅ What We Do to Comply

1. **Dynamic Linking**
   - PySide6 is dynamically linked, not statically compiled into the executable
   - PyInstaller configuration keeps PySide6 as separate shared libraries (.so/.dll files)
   - Users can replace PySide6 libraries without recompiling the application

2. **License Distribution**
   - LGPL-3.0 license information is included in `THIRD_PARTY_LICENSES.md`
   - `LICENSE-NOTICES.txt` is bundled with all distributions
   - Clear attribution to Qt Company and PySide6 project

3. **Source Code Access**
   - Full information about obtaining PySide6 source code is provided
   - Links to official repositories included in documentation
   - Users are informed of their rights under LGPL-3.0

4. **Modification Rights**
   - Documentation explicitly states users can replace PySide6
   - Instructions provided for replacing PySide6 libraries
   - No technical measures prevent library replacement

## For Commercial Use

### ✅ You CAN:
- Use this application commercially
- Distribute the application (source or binary)
- Charge for the application
- Keep your application's source code proprietary
- Modify the application code

### ⚠️ You MUST:
- Keep PySide6 dynamically linked (already done in PyInstaller config)
- Include license notices (automatically included in builds)
- Inform users about PySide6's LGPL-3.0 license
- Allow users to replace PySide6 libraries

### ❌ You CANNOT:
- Statically link PySide6 into the executable
- Remove license notices from distributions
- Prevent users from replacing PySide6 libraries
- Claim PySide6 is your proprietary code

## PyInstaller Configuration

Our `AuthMatrix.spec` file is configured for LGPL compliance:

```python
# PySide6 is kept as separate shared libraries
a = Analysis(
    ['Firesand_Auth_Matrix.py'],
    datas=[
        ('THIRD_PARTY_LICENSES.md', '.'),  # License info included
        ('LICENSE-NOTICES.txt', '.'),       # Notice file included
    ],
    # ... other config
)

# Single-file mode still keeps PySide6 libraries separate
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # PySide6 .so/.dll stay as separate files
    # ... other config
)
```

### How PyInstaller Handles PySide6

- **On Linux**: PySide6 libraries are `.so` files in the distribution folder
- **On Windows**: PySide6 libraries are `.dll` files alongside the .exe
- **On macOS**: PySide6 libraries are in the app bundle's `Frameworks` folder

Users can replace these files with modified versions without any restriction.

## Distribution Checklist

When distributing this application:

- [x] `LICENSE-NOTICES.txt` is included in the distribution
- [x] `THIRD_PARTY_LICENSES.md` is included in the distribution
- [x] PySide6 libraries are separate files (not embedded in executable)
- [x] README.md mentions PySide6 licensing
- [x] Users are informed they can replace PySide6 libraries

## Replacing PySide6

Users who want to replace PySide6 can:

1. **For Python source distributions:**
   ```bash
   pip install PySide6==<desired-version>
   python Firesand_Auth_Matrix.py
   ```

2. **For PyInstaller binary distributions:**
   - Locate the PySide6 library files (.so/.dll) in the distribution folder
   - Replace them with compatible versions
   - The application will use the new libraries

3. **Build from source with custom PySide6:**
   ```bash
   pip install PySide6==<desired-version>
   pyinstaller AuthMatrix.spec
   ```

## Verification

To verify LGPL compliance:

1. **Check Dynamic Linking:**
   ```bash
   # On Linux
   ldd dist/AuthMatrix/AuthMatrix | grep Qt
   
   # On macOS
   otool -L dist/AuthMatrix.app/Contents/MacOS/AuthMatrix | grep Qt
   
   # On Windows
   dumpbin /dependents dist\AuthMatrix\AuthMatrix.exe
   ```

2. **Check License Files:**
   ```bash
   ls dist/AuthMatrix/ | grep -E "LICENSE|THIRD_PARTY"
   ```

3. **Check PySide6 Libraries:**
   ```bash
   # Linux/macOS
   find dist/AuthMatrix/ -name "*.so" -o -name "*.dylib" | grep -i qt
   
   # Windows
   dir /s dist\AuthMatrix\*.dll | findstr Qt
   ```

## Legal Disclaimer

This document provides guidance on LGPL-3.0 compliance based on our implementation. It is not legal advice. For legal questions about licensing, consult with a qualified attorney.

The LGPL-3.0 license text is the authoritative source:
- https://www.gnu.org/licenses/lgpl-3.0.html
- https://www.gnu.org/licenses/gpl-faq.html#LGPLv3

## References

- **LGPL-3.0 License**: https://www.gnu.org/licenses/lgpl-3.0.html
- **PySide6 Licensing**: https://doc.qt.io/qtforpython/licenses.html
- **Qt Licensing**: https://www.qt.io/licensing/
- **PyInstaller Dynamic Libraries**: https://pyinstaller.org/en/stable/operating-mode.html

## Questions?

For questions about licensing compliance:
1. Review the [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) file
2. Check the [LICENSE-NOTICES.txt](LICENSE-NOTICES.txt) file
3. Open an issue at: https://github.com/tes1000/Firesand-AuthMatrix/issues
