#!/usr/bin/env python3
"""
Comprehensive Article Header Fixer
Handles multiple patterns of malformed article headers and consolidates them into proper format.

Fixes patterns like:
FROM:
#### ARTÍCULO 2.-

-

- (VIGENCIA).

TO:
#### ARTÍCULO 2. (VIGENCIA).-

Also fixes:
- Double hashtags (### ### -> ###)
- Extra periods and dashes (..- -> .-)
- Malformed parentheses
"""

import os
import sys
import re
from typing import List, Tuple

class ComprehensiveArticleFixer:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}_COMPREHENSIVE_FIXED.md"
        self.fixes_applied = {
            'malformed_headers': 0,
            'double_hashtags': 0,
            'extra_periods': 0,
            'parentheses_fixes': 0
        }
    
    def read_file(self, file_path: str) -> List[str]:
        """Read file and return lines"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.readlines()
        except Exception as e:
            print(f"Error reading file: {e}")
            return []
    
    def write_file(self, lines: List[str], output_path: str):
        """Write lines to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print(f"File saved to: {output_path}")
        except Exception as e:
            print(f"Error writing file: {e}")
    
    def fix_double_hashtags(self, lines: List[str]) -> List[str]:
        """Fix double hashtags like ### ### ARTÍCULO -> ### ARTÍCULO"""
        fixed_lines = []
        for line in lines:
            original_line = line
            # Fix patterns like "### ### ARTÍCULO" -> "### ARTÍCULO"
            line = re.sub(r'^(#+)\s+\1\s+', r'\1 ', line)
            # Fix patterns like "#### #### ARTÍCULO" -> "#### ARTÍCULO"
            line = re.sub(r'^(#+)\s+(#+)\s+', r'\1 ', line)
            
            if line != original_line:
                self.fixes_applied['double_hashtags'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def fix_extra_periods_and_dashes(self, lines: List[str]) -> List[str]:
        """Fix extra periods and dashes like ..- -> .-"""
        fixed_lines = []
        for line in lines:
            original_line = line
            # Fix patterns like "..-" -> ".-"
            line = re.sub(r'\.\.+-', '.-', line)
            # Fix patterns like ".-.-" -> ".-"
            line = re.sub(r'\.-\.-', '.-', line)
            # Fix patterns like "...-" -> ".-"
            line = re.sub(r'\.{2,}-', '.-', line)
            
            if line != original_line:
                self.fixes_applied['extra_periods'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def fix_parentheses_issues(self, lines: List[str]) -> List[str]:
        """Fix parentheses issues in article headers"""
        fixed_lines = []
        for line in lines:
            original_line = line
            
            # Fix patterns like "(TITLE).)" -> "(TITLE)"
            line = re.sub(r'\(([^)]+)\)\.\)', r'(\1)', line)
            # Fix patterns like "(TITLE)).-" -> "(TITLE).-"
            line = re.sub(r'\(([^)]+)\)\)\.', r'(\1).', line)
            # Fix patterns like "TITLE).-" (missing opening parenthesis) - simplified
            line = re.sub(r'ARTÍCULO\s+(\d+)\.\s+([^(][^)]+)\)\.', r'ARTÍCULO \1. (\2).', line)
            
            if line != original_line:
                self.fixes_applied['parentheses_fixes'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def find_remaining_malformed_patterns(self, lines: List[str]) -> List[Tuple[int, int, str, str]]:
        """Find remaining malformed article patterns"""
        patterns = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for article headers that end with just ".-" (no title)
            article_match = re.match(r'^(#+\s*ARTÍCULO\s+\d+)\.-\s*$', line, re.IGNORECASE)
            if article_match:
                article_prefix = article_match.group(1)
                
                # Look ahead to find the title content
                title_parts = []
                j = i + 1
                found_title = False
                
                # Skip empty lines and standalone dashes
                while j < len(lines) and j < i + 10:
                    next_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not next_line:
                        j += 1
                        continue
                    
                    # Skip standalone dashes
                    if next_line == '-' or re.match(r'^-\s*$', next_line):
                        j += 1
                        continue
                    
                    # Look for title content
                    if (re.match(r'^-\s*\(.*\)', next_line) or 
                        re.match(r'^\(.*\)', next_line) or
                        re.match(r'^-\s*[A-ZÁÉÍÓÚÑ]', next_line)):
                        
                        title_content = next_line
                        title_content = re.sub(r'^-\s*', '', title_content)
                        title_parts.append(title_content)
                        found_title = True
                        j += 1
                        break
                    
                    # If we hit another article or major section, stop
                    if (re.match(r'^#+\s*ARTÍCULO\s+\d+', next_line, re.IGNORECASE) or
                        re.match(r'^#+\s*(CAPÍTULO|SECCIÓN|TÍTULO)', next_line, re.IGNORECASE)):
                        break
                    
                    j += 1
                
                if found_title and title_parts:
                    title_text = ' '.join(title_parts).strip()
                    patterns.append((i, j - 1, article_prefix, title_text))
            
            i += 1
        
        return patterns
    
    def fix_remaining_malformed_headers(self, lines: List[str]) -> List[str]:
        """Fix remaining malformed article headers"""
        patterns = self.find_remaining_malformed_patterns(lines)
        
        if not patterns:
            return lines
        
        print(f"Found {len(patterns)} remaining malformed patterns to fix")
        
        # Apply fixes from bottom to top
        fixed_lines = lines.copy()
        
        for start_line, end_line, article_prefix, title_text in reversed(patterns):
            original_line = lines[start_line]
            hashtag_match = re.match(r'^(#+)', original_line)
            hashtag_level = hashtag_match.group(1) if hashtag_match else '####'
            
            # Clean up the title text
            title_text = title_text.strip()
            
            # Ensure proper parentheses format
            if not title_text.startswith('('):
                title_text = f"({title_text}"
            if not title_text.endswith(')'):
                if title_text.endswith('.'):
                    title_text = title_text[:-1] + ')'
                else:
                    title_text = title_text + ')'
            
            # Create properly formatted header
            new_header = f"{hashtag_level} {article_prefix}. {title_text}.-\n"
            
            # Replace the malformed section
            del fixed_lines[start_line:end_line + 1]
            fixed_lines.insert(start_line, new_header)
            fixed_lines.insert(start_line + 1, '\n')
            
            self.fixes_applied['malformed_headers'] += 1
        
        return fixed_lines
    
    def process(self) -> bool:
        """Main processing function"""
        print("=" * 60)
        print("COMPREHENSIVE ARTICLE HEADER FIXER")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print()
        
        lines = self.read_file(self.input_file)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Apply fixes in sequence
        print("\n1. Fixing double hashtags...")
        lines = self.fix_double_hashtags(lines)
        
        print("2. Fixing extra periods and dashes...")
        lines = self.fix_extra_periods_and_dashes(lines)
        
        print("3. Fixing parentheses issues...")
        lines = self.fix_parentheses_issues(lines)
        
        print("4. Fixing remaining malformed headers...")
        lines = self.fix_remaining_malformed_headers(lines)
        
        print(f"\nFixed file has {len(lines)} lines")
        
        # Print summary
        print("\nFixes applied:")
        total_fixes = 0
        for fix_type, count in self.fixes_applied.items():
            if count > 0:
                print(f"  - {fix_type}: {count}")
                total_fixes += count
        
        print(f"\nTotal fixes applied: {total_fixes}")
        
        self.write_file(lines, self.output_file)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📄 Fixed file: {self.output_file}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_article_fixer.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    fixer = ComprehensiveArticleFixer(input_file, output_file)
    success = fixer.process()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
