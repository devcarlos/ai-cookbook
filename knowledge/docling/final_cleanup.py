#!/usr/bin/env python3
"""
Final Cleanup Script
Handles remaining character encoding issues and final formatting cleanup.
"""

import os
import sys
import re
from typing import List

class FinalCleanup:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}_FINAL.md"
        self.fixes_applied = {
            'character_fixes': 0,
            'accent_fixes': 0,
            'formatting_fixes': 0
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
    
    def fix_character_encoding(self, lines: List[str]) -> List[str]:
        """Fix character encoding issues"""
        fixed_lines = []
        
        # Common character replacements
        replacements = {
            'ARTCULO': 'ARTÍCULO',
            'MBITO': 'ÁMBITO',
            'APLICACIN': 'APLICACIÓN',
            'Cdigo': 'Código',
            'rgimen': 'régimen',
            'jurdico': 'jurídico',
            'carcter': 'carácter',
            'VIGENCIA': 'VIGENCIA',
            'PRELACIN': 'PRELACIÓN',
            'INTERPRETACIN': 'INTERPRETACIÓN',
            'ANALOGA': 'ANALOGÍA',
            'CLASIFICACIN': 'CLASIFICACIÓN',
            'situacin': 'situación',
            'contribuyente': 'contribuyente',
            'realizacin': 'realización',
            'financiacin': 'financiación',
            'obligacin': 'obligación',
            'disposicin': 'disposición',
            'aplicacin': 'aplicación',
            'normativa': 'normativa',
            'territorial': 'territorial',
            'competente': 'competente',
            'establezcan': 'establezcan',
            'restringidos': 'restringidos',
            'publicacin': 'publicación',
            'determinen': 'determinen',
            'hubiera': 'hubiera',
            'previa': 'previa'
        }
        
        for line in lines:
            original_line = line
            
            # Apply character replacements
            for bad, good in replacements.items():
                if bad in line:
                    line = line.replace(bad, good)
                    self.fixes_applied['character_fixes'] += 1
            
            # Fix specific accent issues
            line = re.sub(r'\bARTCULO\b', 'ARTÍCULO', line)
            line = re.sub(r'\bMBITO\b', 'ÁMBITO', line)
            line = re.sub(r'\bAPLICACIN\b', 'APLICACIÓN', line)
            
            if line != original_line:
                self.fixes_applied['accent_fixes'] += 1
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def final_formatting_cleanup(self, lines: List[str]) -> List[str]:
        """Final formatting cleanup"""
        fixed_lines = []
        
        for line in lines:
            original_line = line
            
            # Ensure proper spacing around periods in article headers
            line = re.sub(r'ARTÍCULO\s+(\d+)\s*\.\s*\(', r'ARTÍCULO \1. (', line)
            
            # Fix any remaining double spaces
            line = re.sub(r'  +', ' ', line)
            
            # Ensure proper ending for article headers
            line = re.sub(r'(\([^)]+\))\s*\.\s*([^-])', r'\1. \2', line)
            
            if line != original_line:
                self.fixes_applied['formatting_fixes'] += 1
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def process(self) -> bool:
        """Main processing function"""
        print("=" * 60)
        print("FINAL CLEANUP")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print()
        
        lines = self.read_file(self.input_file)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Apply fixes
        print("\n1. Fixing character encoding issues...")
        lines = self.fix_character_encoding(lines)
        
        print("2. Final formatting cleanup...")
        lines = self.final_formatting_cleanup(lines)
        
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
        print(f"📄 Final file: {self.output_file}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python final_cleanup.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    cleaner = FinalCleanup(input_file, output_file)
    success = cleaner.process()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
