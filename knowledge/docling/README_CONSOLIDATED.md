# PDF to Markdown Processing Pipeline

This directory contains a consolidated, single-script solution for processing PDF documents into clean, well-formatted markdown files.

## Main Script

**`pdf_to_markdown_processor.py`** - Complete PDF to Markdown processing pipeline that handles:

1. **PDF Extraction** - Extracts markdown from PDF files using Docling
2. **Issue Analysis** - Analyzes the extracted markdown for common issues
3. **Comprehensive Fixes** - Applies targeted fixes for legal document formatting
4. **Final Verification** - Verifies the results and provides statistics

## Usage

### Basic Usage
```bash
# Process a PDF file
python pdf_to_markdown_processor.py document.pdf

# Process a markdown file (cleanup only)
python pdf_to_markdown_processor.py document.md

# Specify output file
python pdf_to_markdown_processor.py document.pdf --output final_document.md
```

### Command Line Options
- `input_file` - Input PDF or markdown file to process (required)
- `--output, -o` - Output markdown file path (optional, auto-generated if not specified)
- `--verbose, -v` - Enable verbose output (optional)

## Features

### PDF Processing
- Extracts markdown content from PDF files using Docling
- Handles URL-encoded filenames and special characters
- Creates temporary files for processing

### Markdown Analysis
- Processes files in chunks for memory efficiency
- Identifies common issues:
  - Empty hashtags between sections
  - Unwanted table formatting
  - Missing article headers
  - OCR errors and scattered letters
  - Strange characters
  - Excessive whitespace
  - Incorrect header hierarchy

### Comprehensive Fixes
- **Header Hierarchy**: Applies proper markdown header levels for legal documents
  - CAPÍTULO → `##`
  - SECCIÓN → `##`
  - ARTÍCULO → `###`
  - Disposiciones Relacionadas → `####`
  - Nota del Editor → `####`
  - Referenced articles in special sections → `#####`

- **Text Cleanup**: 
  - Fixes scattered letters (OCR errors)
  - Removes strange characters while preserving important ones
  - Cleans up excessive whitespace
  - Removes table formatting remnants

- **Legal Document Specific**:
  - Proper article formatting with content separation
  - Correct hierarchy for referenced articles
  - Quote prefix removal from article titles

## Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Main dependencies:
- `docling` - For PDF extraction
- `re` - For regex pattern matching
- `argparse` - For command line interface

## Output

The script provides:
- Detailed processing steps with progress indicators
- Statistics on issues found and resolved
- Success rate calculation
- Final processed markdown file

## Example Output

```
============================================================
PDF TO MARKDOWN PROCESSING PIPELINE
============================================================
Input file: document.pdf
Output file: document_processed.md

Step 1: Extracting markdown from PDF...
Step 2: Analyzing markdown for issues...
Analysis complete: 1234 issues found

Step 3: Applying comprehensive fixes...
Fixes applied:
  - header_hierarchy: 150
  - article_formatting: 200
  - scattered_letters: 50
  - strange_characters: 75
  ...

Step 4: Verifying results...

============================================================
PROCESSING COMPLETE
============================================================
Original issues: 1234
Remaining issues: 234
Issues resolved: 1000
Success rate: 81.0%

Final document: document_processed.md
```

## Files Removed

The following files were consolidated into the main script and are no longer needed:
- `process_document.py`
- `batch_analyzer.py` 
- `markdown_fixer.py`
- `apply_fixes_example.py`
- `run_analysis.py`
- `batch_process.py`
- `text_extraction_comparison.py`
- `test_sample.md`
- `test_sample_fixed.md`
- `cleaned_text_for_debugging.txt`

## Other Files

- `1-extraction.py` - Original PDF extraction script (kept for reference)
- `2-chunking.py` - Text chunking utilities
- `3-embedding.py` - Text embedding functionality  
- `4-search.py` - Search functionality
- `5-chat.py` - Chat interface
- `MARKDOWN_FIXING_SOLUTION.md` - Documentation of the fixing approach
- `utils/` - Utility functions
- `data/` - Sample data files
- `output/` - Processed output files
