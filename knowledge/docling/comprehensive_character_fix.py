#!/usr/bin/env python3
"""
Comprehensive Character Fix Script
Handles all character encoding issues in the document.
"""

import os
import sys
import re
from typing import List

class ComprehensiveCharacterFix:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(input_file)[0]}_CHAR_FIXED.md"
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
    
    def fix_all_characters(self, lines: List[str]) -> List[str]:
        """Fix all character encoding issues"""
        fixed_lines = []
        
        # Comprehensive character replacements
        replacements = {
            # Article-related words
            'ARTCULO': 'ARTÍCULO',
            'ARTCULO': 'ARTÍCULO',
            'ARTCULO': 'ARTÍCULO',
            
            # Scope-related words
            'MBITO': 'ÁMBITO',
            'ÁÁMBITO': 'ÁMBITO',
            'AMBITO': 'ÁMBITO',
            
            # Application-related words
            'APLICACIN': 'APLICACIÓN',
            'APLICACION': 'APLICACIÓN',
            'aplicacin': 'aplicación',
            'aplicacion': 'aplicación',
            
            # Code-related words
            'Cdigo': 'Código',
            'CDIGO': 'CÓDIGO',
            'Codigo': 'Código',
            'CODIGO': 'CÓDIGO',
            
            # Regime-related words
            'rgimen': 'régimen',
            'RGIMEN': 'RÉGIMEN',
            'regimen': 'régimen',
            'REGIMEN': 'RÉGIMEN',
            
            # Legal-related words
            'jurdico': 'jurídico',
            'JURDICO': 'JURÍDICO',
            'juridico': 'jurídico',
            'JURIDICO': 'JURÍDICO',
            
            # Character-related words
            'carcter': 'carácter',
            'CARCTER': 'CARÁCTER',
            'caracter': 'carácter',
            'CARACTER': 'CARÁCTER',
            
            # Precedence-related words
            'PRELACIN': 'PRELACIÓN',
            'PRELACION': 'PRELACIÓN',
            'prelacin': 'prelación',
            'prelacion': 'prelación',
            
            # Interpretation-related words
            'INTERPRETACIN': 'INTERPRETACIÓN',
            'INTERPRETACION': 'INTERPRETACIÓN',
            'interpretacin': 'interpretación',
            'interpretacion': 'interpretación',
            
            # Analogy-related words
            'ANALOGA': 'ANALOGÍA',
            'ANALOGIA': 'ANALOGÍA',
            'analoga': 'analogía',
            'analogia': 'analogía',
            
            # Classification-related words
            'CLASIFICACIN': 'CLASIFICACIÓN',
            'CLASIFICACION': 'CLASIFICACIÓN',
            'clasificacin': 'clasificación',
            'clasificacion': 'clasificación',
            
            # Situation-related words
            'situacin': 'situación',
            'SITUACIN': 'SITUACIÓN',
            'situacion': 'situación',
            'SITUACION': 'SITUACIÓN',
            
            # Realization-related words
            'realizacin': 'realización',
            'REALIZACIN': 'REALIZACIÓN',
            'realizacion': 'realización',
            'REALIZACION': 'REALIZACIÓN',
            
            # Financing-related words
            'financiacin': 'financiación',
            'FINANCIACIN': 'FINANCIACIÓN',
            'financiacion': 'financiación',
            'FINANCIACION': 'FINANCIACIÓN',
            
            # Obligation-related words
            'obligacin': 'obligación',
            'OBLIGACIN': 'OBLIGACIÓN',
            'obligacion': 'obligación',
            'OBLIGACION': 'OBLIGACIÓN',
            
            # Disposition-related words
            'disposicin': 'disposición',
            'DISPOSICIN': 'DISPOSICIÓN',
            'disposicion': 'disposición',
            'DISPOSICION': 'DISPOSICIÓN',
            
            # Publication-related words
            'publicacin': 'publicación',
            'PUBLICACIN': 'PUBLICACIÓN',
            'publicacion': 'publicación',
            'PUBLICACION': 'PUBLICACIÓN',
            
            # Administration-related words
            'Administracin': 'Administración',
            'ADMINISTRACIN': 'ADMINISTRACIÓN',
            'Administracion': 'Administración',
            'ADMINISTRACION': 'ADMINISTRACIÓN',
            
            # Nation-related words
            'nacin': 'nación',
            'NACIN': 'NACIÓN',
            'nacion': 'nación',
            'NACION': 'NACIÓN',
            
            # Other common words
            'determinacin': 'determinación',
            'DETERMINACIN': 'DETERMINACIÓN',
            'determinacion': 'determinación',
            'DETERMINACION': 'DETERMINACIÓN',
            
            'informacin': 'información',
            'INFORMACIN': 'INFORMACIÓN',
            'informacion': 'información',
            'INFORMACION': 'INFORMACIÓN',
            
            'organizacin': 'organización',
            'ORGANIZACIN': 'ORGANIZACIÓN',
            'organizacion': 'organización',
            'ORGANIZACION': 'ORGANIZACIÓN',
            
            'resolucin': 'resolución',
            'RESOLUCIN': 'RESOLUCIÓN',
            'resolucion': 'resolución',
            'RESOLUCION': 'RESOLUCIÓN',
            
            'funcin': 'función',
            'FUNCIN': 'FUNCIÓN',
            'funcion': 'función',
            'FUNCION': 'FUNCIÓN',
            
            'jurisdiccin': 'jurisdicción',
            'JURISDICCIN': 'JURISDICCIÓN',
            'jurisdiccion': 'jurisdicción',
            'JURISDICCION': 'JURISDICCIÓN'
        }
        
        for line in lines:
            original_line = line
            
            # Apply all character replacements
            for bad, good in replacements.items():
                if bad in line:
                    line = line.replace(bad, good)
            
            # Additional regex-based fixes for common patterns
            line = re.sub(r'\bARTCULO\b', 'ARTÍCULO', line)
            line = re.sub(r'\bMBITO\b', 'ÁMBITO', line)
            line = re.sub(r'\bAPLICACIN\b', 'APLICACIÓN', line)
            line = re.sub(r'\bCdigo\b', 'Código', line)
            line = re.sub(r'\brgimen\b', 'régimen', line)
            line = re.sub(r'\bjurdico\b', 'jurídico', line)
            line = re.sub(r'\bcarcter\b', 'carácter', line)
            
            if line != original_line:
                self.fixes_applied += 1
            
            fixed_lines.append(line)
        
        return fixed_lines
    
    def process(self) -> bool:
        """Main processing function"""
        print("=" * 60)
        print("COMPREHENSIVE CHARACTER FIX")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file}")
        print()
        
        lines = self.read_file(self.input_file)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Apply character fixes
        print("\nFixing all character encoding issues...")
        lines = self.fix_all_characters(lines)
        
        print(f"Fixed file has {len(lines)} lines")
        print(f"Total character fixes applied: {self.fixes_applied}")
        
        self.write_file(lines, self.output_file)
        
        print(f"\n✅ Processing completed successfully!")
        print(f"📄 Final file: {self.output_file}")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_character_fix.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    fixer = ComprehensiveCharacterFix(input_file, output_file)
    success = fixer.process()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
