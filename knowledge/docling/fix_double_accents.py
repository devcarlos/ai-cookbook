#!/usr/bin/env python3
"""
Fix Double Accents Script
Fixes double accents like ÁÁ -> Á, ÉÉ -> É, etc.
"""

import os
import sys
import re
from typing import List

class DoubleAccentFixer:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}_ACCENT_FIXED.md"
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
    
    def fix_double_accents(self, lines: List[str]) -> List[str]:
        """Fix double accents"""
        fixed_lines = []
        
        # Double accent replacements
        double_accent_fixes = {
            'ÁÁ': 'Á',
            'ÉÉ': 'É', 
            'ÍÍ': 'Í',
            'ÓÓ': 'Ó',
            'ÚÚ': 'Ú',
            'áá': 'á',
            'éé': 'é',
            'íí': 'í',
            'óó': 'ó',
            'úú': 'ú',
            'ÑÑ': 'Ñ',
            'ññ': 'ñ'
        }
        
        # Additional specific fixes
        specific_fixes = {
            'ÁÁMBITO': 'ÁMBITO',
            'ÁAMBITO': 'ÁMBITO',
            'APLICACIÓÓN': 'APLICACIÓN',
            'APLICACIÓN': 'APLICACIÓN',
            'disposiciónes': 'disposiciones',
            'naciónal': 'nacional',
            'internaciónales': 'internacionales',
            'Internaciónales': 'Internacionales'
        }
        
        for line in lines:
            original_line = line
            
            # Apply double accent fixes
            for double, single in double_accent_fixes.items():
                if double in line:
                    line = line.replace(double, single)
            
            # Apply specific fixes
            for bad, good in specific_fixes.items():
                if bad in line:
                    line = line.replace(bad, good)
            
            # Additional regex-based fixes
            line = re.sub(r'Á{2,}', 'Á', line)  # Multiple Á -> single Á
            line = re.sub(r'É{2,}', 'É', line)  # Multiple É -> single É
            line = re.sub(r'Í{2,}', 'Í', line)  # Multiple Í -> single Í
            line = re.sub(r'Ó{2,}', 'Ó', line)  # Multiple Ó -> single Ó
            line = re.sub(r'Ú{2,}', 'Ú', line)  # Multiple Ú -> single Ú
            
            if line != original_line:
                self.fixes_applied += 1
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def process(self) -> bool:
        """Main processing function"""
        print("=" * 60)
        print("DOUBLE ACCENT FIXER")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print()
        
        lines = self.read_file(self.input_file)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Apply fixes
        print("\nFixing double accents...")
        lines = self.fix_double_accents(lines)
        
        print(f"Fixed file has {len(lines)} lines")
        print(f"Total accent fixes applied: {self.fixes_applied}")
        
        self.write_file(lines, self.output_file)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📄 Final file: {self.output_file}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_double_accents.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    fixer = DoubleAccentFixer(input_file, output_file)
    success = fixer.process()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
