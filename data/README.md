# Data Directory

This directory contains reference data and input documents.

## Required Files

### CIS Guide (Reference Data)
- **File**: `cis_guide.pdf`
- **Description**: CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)
- **Purpose**: Source for building the Reference Catalog
- **Download**: Obtain from CIS website (requires internet during setup)

### Sample Policies (Optional)
Place your organizational policy documents here for analysis:
- `*.pdf` - Policy documents in PDF format
- `*.docx` - Policy documents in Word format
- `*.txt` - Policy documents in plain text format

## Notes

- This directory is excluded from git (see `.gitignore`)
- Ensure `cis_guide.pdf` is present before running `build_catalog.py`
- Policy documents should be text-based (OCR not supported)
