#!/usr/bin/env python3
"""
Integration of batch newline processing into the main PDF processor
"""

import re
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ContentBlock:
    content: str
    type: str  # 'title', 'subtitle', 'paragraph', 'empty'
    line_number: int
    newlines_after: int

def classify_content_type(line: str) -> str:
    """Classify a line as title, subtitle, paragraph, or empty"""
    line_stripped = line.strip()
    
    if not line_stripped:
        return 'empty'
    
    # Title patterns
    title_patterns = [
        r'^#+\s+LEY\s+N°',
        r'^#+\s+CÓDIGO\s+TRIBUTARIO',
        r'^#+\s+CAPÍTULO',
        r'^#+\s+SECCIÓN',
        r'^#+\s+TÍTULO',
        r'^#+\s+ANEXO',
        r'^#+\s+Presentación',
    ]
    
    # Subtitle patterns
    subtitle_patterns = [
        r'^#+\s+ARTÍCULO\s+\d+',
        r'^#+\s+Disposiciones\s+Relacionadas',
        r'^#+\s+Nota\s+del\s+Editor',
        r'^#+\s+DECRETOS?\s+SUPREMOS?',
        r'^#+\s+IMPUESTOS\s+NACIONALES',
    ]
    
    # Check for titles
    for pattern in title_patterns:
        if re.search(pattern, line_stripped, re.IGNORECASE):
            return 'title'
    
    # Check for subtitles
    for pattern in subtitle_patterns:
        if re.search(pattern, line_stripped, re.IGNORECASE):
            return 'subtitle'
    
    # Default to paragraph if it has content
    if line_stripped:
        return 'paragraph'
    
    return 'empty'

def process_lines_batch_newlines(lines: List[str], batch_size: int = 100) -> List[str]:
    """Process lines using batch approach to fix newlines intelligently"""
    
    # Convert lines to content blocks
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        content_type = classify_content_type(line)
        
        if content_type == 'empty':
            # Count consecutive empty lines
            empty_count = 0
            for j in range(i, len(lines)):
                if lines[j].strip() == '':
                    empty_count += 1
                else:
                    break
            
            blocks.append(ContentBlock(
                content='',
                type='empty',
                line_number=i + 1,
                newlines_after=empty_count
            ))
            i += empty_count
        else:
            # Count newlines after this content line
            newlines_after = 0
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == '':
                    newlines_after += 1
                else:
                    break
            
            blocks.append(ContentBlock(
                content=line.strip(),
                type=content_type,
                line_number=i + 1,
                newlines_after=newlines_after
            ))
            i += 1
    
    # Define optimal newline rules
    optimal_rules = {
        'title': {'before': 2, 'after': 1},      # Titles need more space before, less after
        'subtitle': {'before': 1, 'after': 1},   # Subtitles need moderate spacing
        'paragraph': {'before': 0, 'after': 1},  # Paragraphs need minimal spacing
    }
    
    # Generate fixed content
    fixed_lines = []
    
    for i, block in enumerate(blocks):
        if block.type == 'empty':
            continue  # Skip empty blocks, we'll add them as needed
        
        # Add optimal newlines before content
        if block.type in optimal_rules:
            newlines_before = optimal_rules[block.type]['before']
            
            # Don't add newlines at the very beginning
            if i > 0 and newlines_before > 0:
                fixed_lines.extend([''] * newlines_before)
        
        # Add the content line
        fixed_lines.append(block.content)
        
        # Add optimal newlines after content
        if block.type in optimal_rules:
            newlines_after = optimal_rules[block.type]['after']
            if newlines_after > 0:
                fixed_lines.extend([''] * newlines_after)
    
    # Convert back to lines with proper line endings
    result_lines = []
    for line in fixed_lines:
        result_lines.append(line + '\n' if line else '\n')
    
    return result_lines

# Test the integration
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_newline_integration.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '_integrated_fix.md')
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Read file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Processing {len(lines)} lines...")
    
    # Process with batch newline fixing
    fixed_lines = process_lines_batch_newlines(lines)
    
    # Write fixed file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"Fixed file saved to: {output_file}")
        print(f"Original lines: {len(lines)}")
        print(f"Fixed lines: {len(fixed_lines)}")
        print("✅ Integration test completed successfully!")
        
    except Exception as e:
        print(f"Error writing file: {e}")
        sys.exit(1)
