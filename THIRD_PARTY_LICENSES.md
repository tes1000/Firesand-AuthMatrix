# Third-Party Licenses

This document contains the licenses for third-party software used in Firesand Auth Matrix.

## PySide6

**License:** LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only  
**Project URL:** https://pyside.org  
**Repository:** https://code.qt.io/cgit/pyside/pyside-setup.git/

PySide6 is the official Python module from the Qt for Python project, which provides access to the complete Qt 6.0+ framework. This application uses PySide6 under the terms of the GNU Lesser General Public License version 3 (LGPL-3.0).

### LGPL-3.0 Compliance

This project complies with the LGPL-3.0 license requirements by:

1. **Dynamic Linking**: PySide6 is dynamically linked (not statically compiled) into the application
2. **Source Code Access**: The complete source code for PySide6 is available at the official repository
3. **License Distribution**: The LGPL-3.0 license text is available online and referenced in all distributions
4. **Attribution**: Proper attribution is provided in documentation and user-facing materials
5. **Modification Rights**: Users can replace the PySide6 library with modified versions

### Using This Software Commercially

Because this application uses PySide6 under LGPL-3.0:

- ✅ You MAY use this software commercially
- ✅ You MAY distribute the application (binary or source)
- ✅ You MAY modify this application's code
- ✅ End users MAY replace the PySide6 library with their own version
- ❌ You do NOT need to release your application's source code under LGPL
- ⚠️ You MUST provide users with the LGPL license text and notices
- ⚠️ You MUST ensure PySide6 remains dynamically linked (not statically compiled)

### PySide6 License Text

The full text of the GNU Lesser General Public License version 3.0 can be found online at:
- https://www.gnu.org/licenses/lgpl-3.0.html
- https://doc.qt.io/qtforpython/licenses.html

### Qt Framework

PySide6 is built on top of the Qt framework. The Qt libraries included with PySide6 are also licensed under LGPL-3.0. The Qt Company provides both open-source (LGPL/GPL) and commercial licenses for Qt.

**More information:**
- Qt Licensing: https://www.qt.io/licensing/
- Qt for Python Licensing: https://doc.qt.io/qtforpython/licenses.html

---

## Other Dependencies

### Requests

**License:** Apache-2.0  
**Repository:** https://github.com/psf/requests

Used for making HTTP requests to test APIs.

### Pillow

**License:** HPND (Historical Permission Notice and Disclaimer)  
**Repository:** https://github.com/python-pillow/Pillow

Used for image processing and icon handling.

---

## License Summary

| Component | License | Commercial Use | Dynamic Linking Required |
|-----------|---------|----------------|-------------------------|
| Firesand Auth Matrix | GPL-3.0 | Yes* | N/A |
| PySide6 | LGPL-3.0 | Yes | Yes |
| Qt Framework | LGPL-3.0 | Yes | Yes |
| Requests | Apache-2.0 | Yes | No |
| Pillow | HPND | Yes | No |

*Note: The main application is GPL-3.0 licensed. When combined with LGPL-3.0 libraries (PySide6), the entire distributed work must comply with GPL-3.0. However, GPL-3.0 permits commercial use.

---

## Attribution Requirements

When distributing this software, you must:

1. Include this `THIRD_PARTY_LICENSES.md` file or provide it upon request
2. Provide a link to the LGPL-3.0 license text (https://www.gnu.org/licenses/lgpl-3.0.html)
3. Provide notice to users that PySide6/Qt is used under LGPL-3.0
4. Inform users they can obtain the PySide6 source code and can replace the library

A ready-to-distribute license notice file is available at `LICENSE-NOTICES.txt`.
