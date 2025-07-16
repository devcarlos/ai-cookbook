#!/usr/bin/env python3
"""
Batch Newline Analyzer and Fixer
Analyzes newline patterns in markdown files and fixes excessive newlines
while preserving document structure.
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

class BatchNewlineAnalyzer:
    def __init__(self, file_path: str, batch_size: int = 100):
        self.file_path = file_path
        self.batch_size = batch_size
        self.content_patterns = {
            'title': [
                r'^#+\s+LEY\s+N°',
                r'^#+\s+CÓDIGO\s+TRIBUTARIO',
                r'^#+\s+CAPÍTULO',
                r'^#+\s+SECCIÓN',
                r'^#+\s+TÍTULO',
                r'^#+\s+ANEXO',
                r'^#+\s+Presentación',
            ],
            'subtitle': [
                r'^#+\s+ARTÍCULO\s+\d+',
                r'^#+\s+Disposiciones\s+Relacionadas',
                r'^#+\s+Nota\s+del\s+Editor',
                r'^#+\s+DECRETOS?\s+SUPREMOS?',
                r'^#+\s+IMPUESTOS\s+NACIONALES',
            ],
            'paragraph': [
                r'^[A-ZÁÉÍÓÚÑ][^#]',  # Starts with capital letter, not a header
                r'^\d+\.',  # Numbered items
                r'^[a-z]',  # Starts with lowercase
                r'^\s*[A-ZÁÉÍÓÚÑ].*[a-záéíóúñ].*$',  # Mixed case content
            ]
        }
    
    def read_file_in_batches(self) -> List[List[str]]:
        """Read file in batches to avoid memory issues"""
        batches = []
        current_batch = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    current_batch.append((line_num, line))
                    
                    if len(current_batch) >= self.batch_size:
                        batches.append(current_batch)
                        current_batch = []
                
                # Add remaining lines
                if current_batch:
                    batches.append(current_batch)
                    
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
        
        return batches
    
    def classify_content(self, line: str) -> str:
        """Classify a line as title, subtitle, paragraph, or empty"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return 'empty'
        
        # Check for titles
        for pattern in self.content_patterns['title']:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return 'title'
        
        # Check for subtitles
        for pattern in self.content_patterns['subtitle']:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return 'subtitle'
        
        # Check for paragraphs
        for pattern in self.content_patterns['paragraph']:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return 'paragraph'
        
        # Default to paragraph if it has content
        if line_stripped:
            return 'paragraph'
        
        return 'empty'
    
    def count_consecutive_newlines(self, lines: List[Tuple[int, str]], start_idx: int) -> int:
        """Count consecutive empty lines starting from start_idx"""
        count = 0
        for i in range(start_idx, len(lines)):
            line_num, line = lines[i]
            if line.strip() == '':
                count += 1
            else:
                break
        return count
    
    def analyze_batch(self, batch: List[Tuple[int, str]]) -> List[ContentBlock]:
        """Analyze a batch of lines and return content blocks"""
        blocks = []
        i = 0
        
        while i < len(batch):
            line_num, line = batch[i]
            content_type = self.classify_content(line)
            
            if content_type == 'empty':
                # Count consecutive empty lines
                empty_count = self.count_consecutive_newlines(batch, i)
                blocks.append(ContentBlock(
                    content='',
                    type='empty',
                    line_number=line_num,
                    newlines_after=empty_count
                ))
                i += empty_count
            else:
                # Count newlines after this content line
                newlines_after = 0
                if i + 1 < len(batch):
                    newlines_after = self.count_consecutive_newlines(batch, i + 1)
                
                blocks.append(ContentBlock(
                    content=line.strip(),
                    type=content_type,
                    line_number=line_num,
                    newlines_after=newlines_after
                ))
                i += 1
        
        return blocks
    
    def analyze_newline_patterns(self) -> Dict[str, Dict[str, int]]:
        """Analyze newline patterns throughout the document"""
        batches = self.read_file_in_batches()
        if not batches:
            return {}
        
        patterns = {
            'title': {'before': [], 'after': []},
            'subtitle': {'before': [], 'after': []},
            'paragraph': {'before': [], 'after': []},
        }
        
        all_blocks = []
        
        print(f"Processing {len(batches)} batches...")
        
        for batch_num, batch in enumerate(batches, 1):
            print(f"  Analyzing batch {batch_num}/{len(batches)}")
            blocks = self.analyze_batch(batch)
            all_blocks.extend(blocks)
        
        # Analyze patterns
        for i, block in enumerate(all_blocks):
            if block.type in patterns:
                # Count newlines after
                patterns[block.type]['after'].append(block.newlines_after)
                
                # Count newlines before (look at previous block)
                if i > 0:
                    prev_block = all_blocks[i-1]
                    if prev_block.type == 'empty':
                        patterns[block.type]['before'].append(prev_block.newlines_after)
                    else:
                        patterns[block.type]['before'].append(0)
        
        # Calculate statistics
        stats = {}
        for content_type in patterns:
            stats[content_type] = {
                'before': {
                    'avg': sum(patterns[content_type]['before']) / len(patterns[content_type]['before']) if patterns[content_type]['before'] else 0,
                    'max': max(patterns[content_type]['before']) if patterns[content_type]['before'] else 0,
                    'min': min(patterns[content_type]['before']) if patterns[content_type]['before'] else 0,
                    'common': max(set(patterns[content_type]['before']), key=patterns[content_type]['before'].count) if patterns[content_type]['before'] else 0
                },
                'after': {
                    'avg': sum(patterns[content_type]['after']) / len(patterns[content_type]['after']) if patterns[content_type]['after'] else 0,
                    'max': max(patterns[content_type]['after']) if patterns[content_type]['after'] else 0,
                    'min': min(patterns[content_type]['after']) if patterns[content_type]['after'] else 0,
                    'common': max(set(patterns[content_type]['after']), key=patterns[content_type]['after'].count) if patterns[content_type]['after'] else 0
                }
            }
        
        return stats, all_blocks
    
    def fix_newlines_batch(self, output_path: str) -> bool:
        """Fix newlines using batch processing with intelligent rules"""
        stats, all_blocks = self.analyze_newline_patterns()
        
        print("\nNewline Pattern Analysis:")
        print("=" * 50)
        for content_type, data in stats.items():
            print(f"{content_type.upper()}:")
            print(f"  Before - Avg: {data['before']['avg']:.1f}, Max: {data['before']['max']}, Common: {data['before']['common']}")
            print(f"  After  - Avg: {data['after']['avg']:.1f}, Max: {data['after']['max']}, Common: {data['after']['common']}")
        
        # Define optimal newline rules based on analysis
        optimal_rules = {
            'title': {'before': 2, 'after': 1},      # Titles need more space before, less after
            'subtitle': {'before': 1, 'after': 1},   # Subtitles need moderate spacing
            'paragraph': {'before': 0, 'after': 1},  # Paragraphs need minimal spacing
        }
        
        print(f"\nApplying optimal newline rules:")
        for content_type, rules in optimal_rules.items():
            print(f"  {content_type}: {rules['before']} before, {rules['after']} after")
        
        # Generate fixed content
        fixed_lines = []
        
        for i, block in enumerate(all_blocks):
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
        
        # Write fixed content
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                for line in fixed_lines:
                    file.write(line + '\n')
            
            print(f"\nFixed file saved to: {output_path}")
            print(f"Original blocks: {len(all_blocks)}")
            print(f"Fixed lines: {len(fixed_lines)}")
            
            return True
            
        except Exception as e:
            print(f"Error writing fixed file: {e}")
            return False

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python batch_newline_analyzer.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.md', '_fixed_newlines.md')
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    analyzer = BatchNewlineAnalyzer(input_file, batch_size=100)
    success = analyzer.fix_newlines_batch(output_file)
    
    if success:
        print("\n✅ Newline fixing completed successfully!")
    else:
        print("\n❌ Newline fixing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
