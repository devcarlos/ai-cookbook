#!/usr/bin/env python3
"""
Article Header Formatting Fixer
Fixes malformed article headers where the title is separated by unwanted dashes and line breaks.

Example fix:
FROM:
#### ARTÍCULO 2.-

-

- (VIGENCIA).

TO:
#### ARTÍCULO 2. (VIGENCIA).-
"""

import os
import sys
import re
from typing import List, Tuple

class ArticleHeaderFixer:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}_HEADER_FIXED.md"
        self.fixes_applied = 0
    
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
    
    def find_malformed_article_patterns(self, lines: List[str]) -> List[Tuple[int, int, str, str]]:
        """
        Find malformed article patterns in the text.
        Returns list of (start_line, end_line, article_header, title_content)
        """
        patterns = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for article headers with just the number and dash
            article_match = re.match(r'^(#+\s*ARTÍCULO\s+\d+)\.-\s*$', line, re.IGNORECASE)
            if article_match:
                article_prefix = article_match.group(1)
                hashtag_level = len(re.match(r'^#+', line).group(0))
                
                # Look ahead to find the title content
                title_parts = []
                j = i + 1
                found_title = False
                
                # Skip empty lines and standalone dashes
                while j < len(lines) and j < i + 10:  # Look ahead max 10 lines
                    next_line = lines[j].strip()
                    
                    # Skip empty lines
                    if not next_line:
                        j += 1
                        continue
                    
                    # Skip standalone dashes
                    if next_line == '-':
                        j += 1
                        continue
                    
                    # Skip lines that are just dashes with spaces
                    if re.match(r'^-\s*$', next_line):
                        j += 1
                        continue
                    
                    # Look for title content (usually in parentheses or starts with dash)
                    if (re.match(r'^-\s*\(.*\)', next_line) or 
                        re.match(r'^\(.*\)', next_line) or
                        re.match(r'^-\s*[A-ZÁÉÍÓÚÑ]', next_line)):
                        
                        # Clean the title content
                        title_content = next_line
                        # Remove leading dash and spaces
                        title_content = re.sub(r'^-\s*', '', title_content)
                        title_parts.append(title_content)
                        found_title = True
                        j += 1
                        break
                    
                    # If we hit another article or major section, stop looking
                    if (re.match(r'^#+\s*ARTÍCULO\s+\d+', next_line, re.IGNORECASE) or
                        re.match(r'^#+\s*(CAPÍTULO|SECCIÓN|TÍTULO)', next_line, re.IGNORECASE)):
                        break
                    
                    j += 1
                
                if found_title and title_parts:
                    title_text = ' '.join(title_parts).strip()
                    patterns.append((i, j - 1, article_prefix, title_text))
            
            i += 1
        
        return patterns
    
    def fix_article_headers(self, lines: List[str]) -> List[str]:
        """Fix malformed article headers"""
        # Find all malformed patterns first
        patterns = self.find_malformed_article_patterns(lines)
        
        if not patterns:
            print("No malformed article patterns found.")
            return lines
        
        print(f"Found {len(patterns)} malformed article patterns to fix:")
        for i, (start_line, end_line, article_prefix, title_text) in enumerate(patterns[:10]):
            print(f"  {i+1}. Line {start_line+1}: {article_prefix}.- + '{title_text}'")
        if len(patterns) > 10:
            print(f"  ... and {len(patterns) - 10} more patterns")
        
        # Apply fixes from bottom to top to avoid line number shifts
        fixed_lines = lines.copy()
        
        for start_line, end_line, article_prefix, title_text in reversed(patterns):
            # Determine the correct hashtag level from the original line
            original_line = lines[start_line]
            hashtag_match = re.match(r'^(#+)', original_line)
            hashtag_level = hashtag_match.group(1) if hashtag_match else '####'
            
            # Create the properly formatted article header
            # Format: #### ARTÍCULO X. (TITLE).-
            if title_text.startswith('(') and title_text.endswith(')'):
                # Title is already in parentheses
                new_header = f"{hashtag_level} {article_prefix}. {title_text}.-\n"
            elif title_text.startswith('(') and not title_text.endswith(')'):
                # Title starts with parentheses but doesn't end with them
                if not title_text.endswith('.'):
                    title_text += ')'
                new_header = f"{hashtag_level} {article_prefix}. {title_text}.-\n"
            else:
                # Title is not in parentheses, add them
                new_header = f"{hashtag_level} {article_prefix}. ({title_text}).-\n"
            
            # Replace the malformed section with the fixed header
            # Remove lines from start_line to end_line (inclusive)
            del fixed_lines[start_line:end_line + 1]
            # Insert the new header
            fixed_lines.insert(start_line, new_header)
            # Add a blank line after the header
            fixed_lines.insert(start_line + 1, '\n')
            
            self.fixes_applied += 1
        
        return fixed_lines
    
    def process(self) -> bool:
        """Main processing function"""
        print("=" * 60)
        print("ARTICLE HEADER FORMATTING FIXER")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print()
        
        # Read the input file
        lines = self.read_file(self.input_file)
        if not lines:
            print("Error: Could not read input file")
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Apply fixes
        print("\nApplying article header fixes...")
        fixed_lines = self.fix_article_headers(lines)
        
        print(f"Fixed file has {len(fixed_lines)} lines")
        print(f"Total fixes applied: {self.fixes_applied}")
        
        # Write the output file
        self.write_file(fixed_lines, self.output_file)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📄 Fixed file: {self.output_file}")
        
        return True

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python fix_article_header_formatting.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    fixer = ArticleHeaderFixer(input_file, output_file)
    success = fixer.process()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
