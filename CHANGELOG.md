# Changelog

All notable changes to the **WebFox Recon Framework** will be documented in this file.

## [4.0.0] - 2026-04-07

### Added
- **Complete GUI Overhaul**: A new Streamlit-based graphical interface with a modern Glassmorphism design system (vibrant gradients, Inter/JetBrains Mono fonts).
- **Lucky Recon Rebranding**: Full rebranding of the framework to "Lucky Recon" across all banners, reports, and code headers.
- **Enhanced Stealth Engine**: Improved Randomized User-Agent rotation and jittered delays to better avoid WAF/IDS detection.
- ** consolidated Reporting**: Standardized output naming as `Lucky_WebFox_Report.html` with a new premium HTML structure.
- **Port Scanner Categories**: Enhanced reporting of port findings by risk level and service banner details.

### Changed
- **Installation Script**: Modernized `install.sh` with a startup quick-reference menu and better environment detection for Termux vs Linux.
- **Performance Optimization**: Improved thread handling in core modules for faster data collection.
- **Documentation**: Consolidated README and SECURITY policies to reflect v4.0 standards.

### Fixed
- **Missing File Guards**: Resolved an issue in the GUI where opening a target report would crash if partial results (like snapshots or live subdomains) were missing.
- **Version Inconsistencies**: Standardized versioning strings across all core files to `v4.0`.
- **Report Path Handling**: Fixed a bug where report files would sometimes save with inconsistent folder naming.

---
*Note: This is a major update focused on user experience and brand consolidation.*
