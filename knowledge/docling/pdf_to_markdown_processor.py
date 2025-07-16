#!/usr/bin/env python3
"""
Complete PDF to Markdown Processing Pipeline
This script handles the entire workflow:
1. Extract markdown from PDF files using Docling
2. Analyze the extracted markdown for common issues
3. Apply comprehensive fixes and cleanup
4. Generate final processed markdown file

Usage:
    python pdf_to_markdown_processor.py <input_pdf_file> [output_file.md]
    python pdf_to_markdown_processor.py <input_md_file> [output_file.md]
"""

import os
import sys
import re
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, unquote
import argparse

# Import docling for PDF extraction
try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Error: docling not installed. Please install with: pip install docling")
    sys.exit(1)

@dataclass
class AnalysisResult:
    chunk_number: int
    line_start: int
    line_end: int
    issues: List[Dict]
    suggestions: List[str]

class PDFToMarkdownProcessor:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file
        self.temp_md_file = None
        self.converter = DocumentConverter()
        self.fixes_applied = {
            'empty_hashtags': 0,
            'header_hierarchy': 0,
            'article_formatting': 0,
            'scattered_letters': 0,
            'strange_characters': 0,
            'excessive_whitespace': 0,
            'dash_separators': 0,
            'incorrect_hashtags': 0,
            'table_hashtag_fixes': 0,
            'article_quote_prefix_fixes': 0,
            'reference_hashtag_fixes': 0,
            'article_hierarchy_fixes': 0,
            'incorrect_five_hashtag_fixes': 0
        }
    
    def generate_filename_from_path(self, file_path: str) -> str:
        """Generate a clean filename from a file path"""
        # Get the filename without extension
        filename = os.path.splitext(os.path.basename(file_path))[0]
        
        # URL decode to handle encoded characters
        filename = unquote(filename)
        
        # Replace problematic characters with safe alternatives
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[°]', 'deg', filename)
        filename = re.sub(r'[ñÑ]', 'n', filename)
        filename = re.sub(r'[áàäâ]', 'a', filename)
        filename = re.sub(r'[éèëê]', 'e', filename)
        filename = re.sub(r'[íìïî]', 'i', filename)
        filename = re.sub(r'[óòöô]', 'o', filename)
        filename = re.sub(r'[úùüû]', 'u', filename)
        
        # Remove multiple consecutive underscores and spaces
        filename = re.sub(r'[_\s]+', '_', filename)
        filename = filename.strip('_.')
        
        if not filename:
            filename = "document"
        
        return filename
    
    def extract_markdown_from_pdf(self) -> str:
        """Extract markdown content from PDF file"""
        print(f"Extracting markdown from PDF: {self.input_file}")
        
        try:
            # Convert PDF to document
            result = self.converter.convert(self.input_file)
            document = result.document
            
            # Export to markdown
            markdown_content = document.export_to_markdown()
            
            # Save temporary markdown file for processing
            base_filename = self.generate_filename_from_path(self.input_file)
            self.temp_md_file = f"temp_{base_filename}.md"
            
            with open(self.temp_md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"Markdown extracted successfully. Temporary file: {self.temp_md_file}")
            return self.temp_md_file
            
        except Exception as e:
            print(f"Error extracting markdown from PDF: {e}")
            return None
    
    def is_pdf_file(self, file_path: str) -> bool:
        """Check if the input file is a PDF"""
        return file_path.lower().endswith('.pdf')
    
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
    
    def analyze_markdown_issues(self, file_path: str, chunk_size: int = 500) -> List[AnalysisResult]:
        """Analyze markdown file for common issues"""
        print(f"Analyzing markdown file: {file_path}")
        
        lines = self.read_file(file_path)
        if not lines:
            return []
        
        # Process in chunks
        chunks = []
        for i in range(0, len(lines), chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunks.append((i + 1, chunk_lines))
        
        results = []
        for chunk_num, (line_start, chunk_lines) in enumerate(chunks, 1):
            result = self.analyze_chunk(chunk_num, line_start, chunk_lines)
            results.append(result)
        
        return results
    
    def analyze_chunk(self, chunk_number: int, line_start: int, lines: List[str]) -> AnalysisResult:
        """Analyze a single chunk for all issues"""
        all_issues = []
        suggestions = []
        
        # Run all analysis functions
        all_issues.extend(self.analyze_empty_hashtags(lines))
        all_issues.extend(self.analyze_table_formatting(lines))
        all_issues.extend(self.analyze_article_sections(lines))
        all_issues.extend(self.analyze_text_quality(lines))
        all_issues.extend(self.analyze_new_requirements(lines))
        
        # Generate suggestions based on issues found
        issue_types = set(issue['type'] for issue in all_issues)
        
        if 'empty_hashtag' in issue_types:
            suggestions.append("Remove empty hashtag lines")
        if 'table_formatting' in issue_types or 'dash_separator' in issue_types:
            suggestions.append("Clean up table formatting remnants")
        if 'missing_article_header' in issue_types:
            suggestions.append("Add ## headers to ARTICLE sections")
        if any(t in issue_types for t in ['scattered_letters', 'strange_characters', 'excessive_whitespace']):
            suggestions.append("Clean up OCR/extraction errors")
        
        return AnalysisResult(
            chunk_number=chunk_number,
            line_start=line_start,
            line_end=line_start + len(lines) - 1,
            issues=all_issues,
            suggestions=suggestions
        )
    
    def analyze_empty_hashtags(self, lines: List[str]) -> List[Dict]:
        """Find empty hashtags between sections"""
        issues = []
        for i, line in enumerate(lines):
            if re.match(r'^#+\s*$', line.strip()):
                issues.append({
                    'type': 'empty_hashtag',
                    'line': i + 1,
                    'content': line.strip(),
                    'description': 'Empty hashtag found'
                })
        return issues
    
    def analyze_table_formatting(self, lines: List[str]) -> List[Dict]:
        """Find unwanted table formatting strings with dashes"""
        issues = []
        for i, line in enumerate(lines):
            if re.match(r'^[\s\-\|]+$', line.strip()) and len(line.strip()) > 10:
                issues.append({
                    'type': 'table_formatting',
                    'line': i + 1,
                    'content': line.strip(),
                    'description': 'Unwanted table formatting with dashes'
                })
            
            if re.search(r'\-{5,}', line) and '|' not in line:
                issues.append({
                    'type': 'dash_separator',
                    'line': i + 1,
                    'content': line.strip(),
                    'description': 'Long dash separator (possibly table remnant)'
                })
        return issues
    
    def analyze_article_sections(self, lines: List[str]) -> List[Dict]:
        """Find ARTICLE sections that need ## hashtags"""
        issues = []
        for i, line in enumerate(lines):
            if re.search(r'\bARTICLE\b|\bARTÍCULO\b|\bArt\.\s*\d+', line, re.IGNORECASE):
                if not line.strip().startswith('#'):
                    issues.append({
                        'type': 'missing_article_header',
                        'line': i + 1,
                        'content': line.strip(),
                        'description': 'ARTICLE section without ## header'
                    })
        return issues
    
    def analyze_text_quality(self, lines: List[str]) -> List[Dict]:
        """Find incoherent words and text quality issues"""
        issues = []
        
        ocr_patterns = [
            r'\b[a-zA-Z]{1,2}\b\s+\b[a-zA-Z]{1,2}\b',
            r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\"\']+',
            r'\b\w*[0-9]+\w*[a-zA-Z]+\w*\b',
            r'\s{3,}',
            r'\.{3,}',
        ]
        
        for i, line in enumerate(lines):
            if re.search(ocr_patterns[0], line):
                issues.append({
                    'type': 'scattered_letters',
                    'line': i + 1,
                    'content': line.strip()[:100] if len(line.strip()) > 100 else line.strip(),
                    'description': 'Scattered single/double letters (OCR error)'
                })
            
            strange_chars = re.findall(ocr_patterns[1], line)
            if strange_chars:
                issues.append({
                    'type': 'strange_characters',
                    'line': i + 1,
                    'content': line.strip()[:100] if len(line.strip()) > 100 else line.strip(),
                    'description': f'Strange characters found: {strange_chars[:5]}'
                })
            
            if re.search(ocr_patterns[3], line):
                issues.append({
                    'type': 'excessive_whitespace',
                    'line': i + 1,
                    'content': line.strip()[:100] if len(line.strip()) > 100 else line.strip(),
                    'description': 'Excessive whitespace found'
                })
        
        return issues
    
    def analyze_new_requirements(self, lines: List[str]) -> List[Dict]:
        """Find issues based on new requirements"""
        issues = []
        in_nota_del_editor = False
        in_disposiciones_relacionadas = False
        
        for i, line in enumerate(lines):
            if re.search(r'####\s*Nota\s+del\s+Editor', line, re.IGNORECASE):
                in_nota_del_editor = True
                in_disposiciones_relacionadas = False
                continue
            elif re.search(r'####\s*Disposiciones\s+Relacionadas', line, re.IGNORECASE):
                in_disposiciones_relacionadas = True
                in_nota_del_editor = False
                continue
            elif re.search(r'^###\s+ARTÍCULO\s+\d+', line, re.IGNORECASE):
                in_nota_del_editor = False
                in_disposiciones_relacionadas = False
            elif re.search(r'^##\s+(SECCIÓN|CAPÍTULO|TÍTULO)', line, re.IGNORECASE):
                in_nota_del_editor = False
                in_disposiciones_relacionadas = False
            
            if re.search(r'##\s*\|\s*DECRETOS\s+SUPREMOS', line, re.IGNORECASE):
                issues.append({
                    'type': 'table_hashtag_error',
                    'line': i + 1,
                    'content': line.strip(),
                    'description': 'Hashtags incorrectly applied to table content'
                })
            
            if re.search(r"'\s*ARTÍCULO\s+\d+", line, re.IGNORECASE):
                issues.append({
                    'type': 'article_quote_prefix',
                    'line': i + 1,
                    'content': line.strip(),
                    'description': 'Article title has unwanted quote prefix'
                })
            
            if line.strip().startswith('#####'):
                is_valid_five_hashtag = False
                if (in_nota_del_editor or in_disposiciones_relacionadas) and re.search(r'ARTÍCULO\s+\d+', line, re.IGNORECASE):
                    is_valid_five_hashtag = True
                
                if not is_valid_five_hashtag:
                    issues.append({
                        'type': 'incorrect_five_hashtags',
                        'line': i + 1,
                        'content': line.strip(),
                        'description': 'Line has 5 hashtags but should not'
                    })
        
        return issues
    
    def fix_empty_hashtags(self, lines: List[str]) -> List[str]:
        """Remove empty hashtag lines"""
        fixed_lines = []
        for line in lines:
            if re.match(r'^#+\s*$', line.strip()):
                self.fixes_applied['empty_hashtags'] += 1
                continue
            fixed_lines.append(line)
        return fixed_lines
    
    def fix_header_hierarchy(self, lines: List[str]) -> List[str]:
        """Fix header hierarchy for legal documents according to specifications"""
        fixed_lines = []
        i = 0
        in_table_section = False
        in_disposiciones_relacionadas = False
        in_nota_del_editor = False
        
        while i < len(lines):
            line = lines[i]
            clean_line = re.sub(r'^#+\s*', '', line.strip())
            
            if not clean_line:
                fixed_lines.append(line)
                i += 1
                continue
            
            if re.search(r'3\.\-\s*TABLA\s+DE\s+CORRESPONDENCIAS\s*:', clean_line, re.IGNORECASE):
                in_table_section = True
                fixed_lines.append(f"## {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            if in_table_section and re.search(r'^(ANEXO|DECRETO|LEY\s+N°|IMPUESTOS\s+NACIONALES)', clean_line, re.IGNORECASE):
                in_table_section = False
            
            if in_table_section:
                if line.strip().startswith('#'):
                    fixed_lines.append(f"{clean_line}\n")
                    self.fixes_applied['incorrect_hashtags'] += 1
                else:
                    fixed_lines.append(line)
                i += 1
                continue
            
            # Track if we're in Disposiciones Relacionadas or Nota del Editor sections
            if re.search(r'\bDisposiciones\s+Relacionadas\s*:', clean_line, re.IGNORECASE):
                in_disposiciones_relacionadas = True
                in_nota_del_editor = False
                fixed_lines.append(f"#### {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            if re.search(r'\bNota\s+del\s+Editor\s*:', clean_line, re.IGNORECASE):
                in_nota_del_editor = True
                in_disposiciones_relacionadas = False
                fixed_lines.append(f"#### {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            # Exit reference sections when we encounter a new main article or major section
            if re.search(r'^ARTÍCULO\s+\d+\.\s*[A-Z]', clean_line, re.IGNORECASE) or re.search(r'^(SUJETOS|NACIMIENTO|BASE\s+IMPONIBLE|CAPÍTULO)', clean_line, re.IGNORECASE):
                in_disposiciones_relacionadas = False
                in_nota_del_editor = False
            
            # FIX 1: Handle title order issue - fix "843 LEY N°" to "LEY N° 843"
            title_order_match = re.search(r'^(\d+)\s+(LEY\s+N°)\s*$', clean_line, re.IGNORECASE)
            if title_order_match:
                number = title_order_match.group(1)
                ley_part = title_order_match.group(2)
                corrected_title = f"{ley_part} {number}"
                if line.strip().startswith('#'):
                    # Preserve the hashtag level
                    hashtag_match = re.match(r'^(#+)\s*', line)
                    if hashtag_match:
                        hashtag_level = hashtag_match.group(1)
                        fixed_lines.append(f"{hashtag_level} {corrected_title}\n")
                    else:
                        fixed_lines.append(f"# {corrected_title}\n")
                else:
                    fixed_lines.append(f"# {corrected_title}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            legitimate_headers = [
                r'^LEY\s+N°?\s*\d+',
                r'^Presentación$',
                r'^RESUELVE\s*:?$',
                r'^VISTOS\s*:?$',
                r'^CONSIDERANDO$',
                r'^POR\s+TANTO$',
                r'^Aclaraciones\s+y\s+Referencias\s+Genéricas$',
                r'^\d+\.\-\s+PARA\s+UNA\s+ADECUADA',
                r'^\d+\.\-\s+ACLARACIONES\s*:?$',
                r'^\d+\.\-\s+TABLA\s+DE\s+CORRESPONDENCIAS\s*:?$',
                r'^ANEXO\s+[IVX]+$',
                r'^DECRETOS?\s+SUPREMOS?',
                r'^IMPUESTOS\s+NACIONALES$'
            ]
            
            is_legitimate_header = any(re.search(pattern, clean_line, re.IGNORECASE) for pattern in legitimate_headers)
            
            if is_legitimate_header and line.strip().startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Apply hierarchy rules
            if re.search(r'\bCAPÍTULO\b', clean_line, re.IGNORECASE):
                fixed_lines.append(f"## {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            if re.search(r'\bDISPOSICIONES\s+PRELIMINARES\b', clean_line, re.IGNORECASE):
                fixed_lines.append(f"## {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            if re.search(r'\bSECCIÓN\b', clean_line, re.IGNORECASE):
                fixed_lines.append(f"## {clean_line}\n")
                self.fixes_applied['header_hierarchy'] += 1
                i += 1
                continue
            
            # Handle different article patterns
            # Pattern 1: "ARTÍCULO 1.Créase en" -> "### ARTÍCULO 1.-" + content
            article_match1 = re.search(r'\b(ARTÍCULO\s+\d+)\.(.+)', clean_line, re.IGNORECASE)
            # Pattern 2: "ARTÍCULO 2.A los fines" -> "### ARTÍCULO 2.-" + content  
            article_match2 = re.search(r'\b(ARTÍCULO\s+\d+)\.([A-Z].+)', clean_line, re.IGNORECASE)
            # Pattern 3: Standard format with parentheses "ARTÍCULO 1.- (OBJETO)."
            article_match3 = re.search(r'\b(ARTÍCULO\s+\d+.*?\)\.\s*)(.*)', clean_line, re.IGNORECASE)
            
            if article_match1 or article_match2:
                # Handle patterns where article number is followed by period and immediate content
                match = article_match1 or article_match2
                article_number = match.group(1).strip()
                article_content = match.group(2).strip()
                
                # Format as "### ARTÍCULO X.-" or "#### ARTÍCULO X.-" depending on context
                article_header = f"{article_number}.-"
                
                # Use 4 hashtags if we're in a reference section, 3 otherwise
                if in_disposiciones_relacionadas or in_nota_del_editor:
                    fixed_lines.append(f"#### {article_header}\n")
                else:
                    fixed_lines.append(f"### {article_header}\n")
                
                fixed_lines.append(f"\n")  # Add blank line
                
                if article_content:
                    fixed_lines.append(f"{article_content}\n")
                
                self.fixes_applied['article_formatting'] += 1
                i += 1
                continue
            elif article_match3:
                # Handle standard format with parentheses
                article_header = article_match3.group(1).strip()
                article_content = article_match3.group(2).strip()
                
                # Use 4 hashtags if we're in a reference section, 3 otherwise
                if in_disposiciones_relacionadas or in_nota_del_editor:
                    fixed_lines.append(f"#### {article_header}\n")
                else:
                    fixed_lines.append(f"### {article_header}\n")
                
                fixed_lines.append(f"\n")  # Add blank line
                
                if article_content:
                    fixed_lines.append(f"{article_content}\n")
                
                self.fixes_applied['article_formatting'] += 1
                i += 1
                continue
            
            if line.strip().startswith('#') and not is_legitimate_header and not re.search(r'\b(CAPÍTULO|DISPOSICIONES|SECCIÓN|ARTÍCULO|Disposiciones\s+Relacionadas|Nota\s+del\s+Editor)\b', clean_line, re.IGNORECASE):
                fixed_lines.append(f"{clean_line}\n")
                self.fixes_applied['incorrect_hashtags'] += 1
                i += 1
                continue
            
            fixed_lines.append(line)
            i += 1
        
        return fixed_lines
    
    def fix_scattered_letters(self, lines: List[str]) -> List[str]:
        """Fix scattered single/double letters (OCR errors)"""
        fixed_lines = []
        for line in lines:
            original_line = line
            
            line = re.sub(r'\b([a-zA-ZáéíóúÁÉÍÓÚñÑ])\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ])\b', r'\1\2', line)
            
            ocr_fixes = {
                r'\bE l\b': 'El',
                r'\bL a\b': 'La',
                r'\bD e\b': 'De',
                r'\bE n\b': 'En',
                r'\bA l\b': 'Al',
                r'\bD el\b': 'Del',
                r'\bL os\b': 'Los',
                r'\bL as\b': 'Las',
                r'\bU n\b': 'Un',
                r'\bU na\b': 'Una',
                r'\bS e\b': 'Se',
                r'\bN o\b': 'No',
                r'\bY\s+a\b': 'Ya',
                r'\bS i\b': 'Si',
                r'\bO\s+r\b': 'Or',
            }
            
            for pattern, replacement in ocr_fixes.items():
                if re.search(pattern, line):
                    line = re.sub(pattern, replacement, line)
            
            legal_fixes = {
                r'\bA r t í c u l o\b': 'Artículo',
                r'\bA R T Í C U L O\b': 'ARTÍCULO',
                r'\bC ó d i g o\b': 'Código',
                r'\bT r i b u t a r i o\b': 'Tributario',
                r'\bA d m i n i s t r a c i ó n\b': 'Administración',
                r'\bI m p u e s t o s\b': 'Impuestos',
                r'\bN a c i o n a l e s\b': 'Nacionales',
            }
            
            for pattern, replacement in legal_fixes.items():
                if re.search(pattern, line, re.IGNORECASE):
                    line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
            
            if line != original_line:
                self.fixes_applied['scattered_letters'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def clean_text_line_safe(self, text: str) -> str:
        """Line-safe text cleaning that doesn't affect newlines"""
        
        # 1. Remove unwanted header/footer patterns
        unwanted_patterns = [
            r"<!-- image -->",  # Remove image placeholders from markdown
            r"Prohibida su reproducción impresa o digital sin autorización",
            r"Distribucion Gratuita",
            r"PLAN ÚNICO DE CUENTAS TRIBUTARIO2",
            r"Acceso a Información\s+Tributaria\s+DIGITAL",
            r"www\.impuestos\.gob\.bo",
            r"Línea Gratuita de\s+Consultas Tributarias",
            r"\d{3}-\d{2}-\d{4}",
            r"Texto informativo, para\s+fines legales remitirse a\s+las disposiciones oficiales\.",
            r"TÍTULO\s+[IVXLCDM]+\s+NORMAS\s+SUSTANTIV\s*AS\s+Y\s+MATERIALES",
            r"CÓDIGO TRIBUTARIO BOLIVIANO\s+Y DECRETOS REGLAMENTARIOS",
            r"TEXTO ORDENADO, COMPLEMENTADO\s+Y ACTUALIZADO AL",
            r"CÓDIGO TRIBUTARIO BOLIVIANO\s*LEY N°",
            r"2492\s*2492\s*\d{1,2}/\d{1,2}/\d{4}", # The problematic header
        ]
        for pattern in unwanted_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)

        # 2. Fix misencoded characters and ligatures
        replacements = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú', 'Ã±': 'ñ',
            'Á': 'Á', 'É': 'É', 'Í': 'Í', 'Ó': 'Ó', 'Ú': 'Ú', 'Ñ': 'Ñ',
            'ﬁ': 'fi', 'ﬂ': 'fl',
            'SUSTANTIV AS': 'SUSTANTIVAS' # Specific typo fix
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)

        # 3. Remove control characters except tab and newline
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # 4. Insert spaces to fix stuck words
        # Lowercase letter followed by uppercase (e.g. "boLínea" -> "bo Línea")
        text = re.sub(r'([a-z\.])([A-Z])', r'\1 \2', text)
        # Letter followed by number (e.g. "Tributarias800" -> "Tributarias 800")
        text = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚñÑ])(\d)', r'\1 \2', text)
        # Number followed by letter (e.g. "2492CÓDIGO" -> "2492 CÓDIGO")
        text = re.sub(r'(\d)([a-zA-ZáéíóúÁÉÍÓÚñÑ])', r'\1 \2', text)

        # 5. Fix spacing in initials (e.g. P . O . -> P. O.)
        text = re.sub(r'\b([A-Z])\s+\.\s*', r'\1. ', text)

        # 6. Normalize internal whitespace (multiple spaces/tabs to single space)
        text = re.sub(r'[ \t]+', ' ', text)
        
        return text.strip()

    def clean_text(self, text: str) -> str:
        """Comprehensive text cleaning with improvements for accents and legal codes."""
        
        # 1. Remove unwanted header/footer patterns
        # This is done first to prevent them from joining with valid text.
        unwanted_patterns = [
            r"<!-- image -->",  # Remove image placeholders from markdown
            r"Prohibida su reproducción impresa o digital sin autorización",
            r"Distribucion Gratuita",
            r"PLAN ÚNICO DE CUENTAS TRIBUTARIO2",
            r"ÍNDICE",
            r"Acceso a Información\s+Tributaria\s+DIGITAL",
            r"www\.impuestos\.gob\.bo",
            r"Línea Gratuita de\s+Consultas Tributarias",
            r"\d{3}-\d{2}-\d{4}",
            r"Texto informativo, para\s+fines legales remitirse a\s+las disposiciones oficiales\.",
            r"TÍTULO\s+[IVXLCDM]+\s+NORMAS\s+SUSTANTIV\s*AS\s+Y\s+MATERIALES",
            r"CÓDIGO TRIBUTARIO BOLIVIANO\s+Y DECRETOS REGLAMENTARIOS",
            r"TEXTO ORDENADO, COMPLEMENTADO\s+Y ACTUALIZADO AL",
            r"CÓDIGO TRIBUTARIO BOLIVIANO\s*LEY N°",
            r"^\s*Ley N° \d+\s*$", # Lines that only contain "Ley N° XXX"
            r"^\s*[IVXLCDM]+\s*$", # Lines that are only Roman numerals (footers)
            r"^\s*\d{1,3}\s*$", # Lines that are only page numbers
            r"2492\s*2492\s*\d{1,2}/\d{1,2}/\d{4}", # The problematic header
        ]
        for pattern in unwanted_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.MULTILINE)

        # 2. Fix misencoded characters and ligatures
        replacements = {
            'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú', 'Ã±': 'ñ',
            'Á': 'Á', 'É': 'É', 'Í': 'Í', 'Ó': 'Ó', 'Ú': 'Ú', 'Ñ': 'Ñ',
            'ﬁ': 'fi', 'ﬂ': 'fl',
            'SUSTANTIV AS': 'SUSTANTIVAS' # Specific typo fix
        }
        for bad, good in replacements.items():
            text = text.replace(bad, good)

        # 3. Remove control characters except tab and newline
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

        # 4. Insert spaces to fix stuck words
        # Lowercase letter followed by uppercase (e.g. "boLínea" -> "bo Línea")
        text = re.sub(r'([a-z\.])([A-Z])', r'\1 \2', text)
        # Letter followed by number (e.g. "Tributarias800" -> "Tributarias 800")
        text = re.sub(r'([a-zA-ZáéíóúÁÉÍÓÚñÑ])(\d)', r'\1 \2', text)
        # Number followed by letter (e.g. "2492CÓDIGO" -> "2492 CÓDIGO")
        text = re.sub(r'(\d)([a-zA-ZáéíóúÁÉÍÓÚñÑ])', r'\1 \2', text)

        # 5. Repair codes broken by line breaks, e.g. RND-10-\n0021-16 → RND-10-0021-16
        text = re.sub(r'(\b[RDN]{2,3}-?\d+)[\s\n\-]+(\d{4,}-\d{2}\b)', r'\1-\2', text)

        # 6. Join words cut by line break with hyphen, e.g. "au-\ntorización" → "autorización"
        text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

        # 7. Fix spacing in initials (e.g. P . O . -> P. O.)
        text = re.sub(r'\b([A-Z])\s+\.\s*', r'\1. ', text)

        # 8. Conservative newline cleanup - preserve document structure
        return self.clean_newlines_conservative(text)
    
    def classify_content_type(self, line: str) -> str:
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

    def clean_newlines_conservative(self, text: str) -> str:
        """Batch-based intelligent newline cleaning that preserves document structure"""
        from dataclasses import dataclass
        
        @dataclass
        class ContentBlock:
            content: str
            type: str
            line_number: int
            newlines_after: int
        
        lines = text.split('\n')
        
        # Convert lines to content blocks
        blocks = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            content_type = self.classify_content_type(line)
            
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
        
        # Join back to text
        result = '\n'.join(fixed_lines)
        
        # Remove sequences of more than 4 dots (likely formatting artifacts)
        result = re.sub(r'\.{5,}', '...', result)
        
        # Normalize internal whitespace (multiple spaces/tabs to single space)
        result = re.sub(r'[ \t]+', ' ', result)
        
        return result.strip()
    
    def fix_strange_characters(self, lines: List[str]) -> List[str]:
        """Clean up strange characters using comprehensive text cleaning"""
        fixed_lines = []
        for i, line in enumerate(lines):
            original_line = line
            
            # Check if this line is in a table section and should be protected
            if self.is_in_table_section(lines, i) and self.is_table_line(line):
                # Protect table lines from character modifications
                fixed_lines.append(original_line)
                continue
            
            # Apply line-safe text cleaning to each line
            # But we need to preserve the newline character if it exists
            has_newline = line.endswith('\n')
            line_content = line.rstrip('\n')
            
            # Apply clean_text_line_safe to the line content (doesn't affect newlines)
            cleaned_content = self.clean_text_line_safe(line_content)
            
            # Restore the newline if it was there originally
            if has_newline:
                line = cleaned_content + '\n'
            else:
                line = cleaned_content
            
            # Additional character fixes specific to line-by-line processing
            line = re.sub(r'Nº', 'N°', line)
            line = re.sub(r'N\s*°', 'N°', line)
            line = re.sub(r'\(…\)', '', line)
            line = re.sub(r'["""]', '"', line)
            line = re.sub(r"[''']", "'", line)
            line = re.sub(r'–', '-', line)
            line = re.sub(r'—', '-', line)
            
            if line != original_line:
                self.fixes_applied['strange_characters'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def fix_excessive_whitespace(self, lines: List[str]) -> List[str]:
        """Fix excessive whitespace issues"""
        fixed_lines = []
        for i, line in enumerate(lines):
            original_line = line
            
            # IMPROVED: Check if this line is a table line (has pipe characters)
            # Protect ALL table lines from whitespace modifications
            if self.is_table_line(line):
                # Protect table lines from whitespace modifications
                fixed_lines.append(original_line)
                continue
            
            line = re.sub(r' {2,}', ' ', line)
            line = re.sub(r'\t+', ' ', line)
            line = line.rstrip() + '\n' if line.endswith('\n') else line.rstrip()
            
            if line != original_line:
                self.fixes_applied['excessive_whitespace'] += 1
            
            fixed_lines.append(line)
        return fixed_lines
    
    def fix_dash_separators(self, lines: List[str]) -> List[str]:
        """Remove unwanted dash separators (table remnants) while preserving legitimate table separators"""
        fixed_lines = []
        for line in lines:
            # Check if this is a legitimate markdown table separator
            # Pattern: |---|---|---| or |-----|-----|-----|
            if self.is_legitimate_table_separator(line):
                # This is a legitimate table separator, keep it
                fixed_lines.append(line)
                continue
            
            # Remove lines that are only dashes and pipes but NOT legitimate table separators
            if re.match(r'^[\s\-\|]+$', line.strip()) and len(line.strip()) > 10:
                self.fixes_applied['dash_separators'] += 1
                continue
            
            # Remove long dash sequences that are not in tables and have no words
            if re.search(r'\-{5,}', line) and '|' not in line and not re.search(r'\w', line):
                self.fixes_applied['dash_separators'] += 1
                continue
            
            fixed_lines.append(line)
        return fixed_lines
    
    def is_legitimate_table_separator(self, line: str) -> bool:
        """Check if a line is a legitimate markdown table separator"""
        stripped = line.strip()
        
        # Must start and end with |
        if not (stripped.startswith('|') and stripped.endswith('|')):
            return False
        
        # Must contain only |, -, and spaces
        if not re.match(r'^[\|\-\s]+$', stripped):
            return False
        
        # Must have at least 2 columns (at least 3 | characters)
        if stripped.count('|') < 3:
            return False
        
        # Split by | and check each column separator
        parts = stripped.split('|')[1:-1]  # Remove empty first and last parts
        
        # Each part should be only dashes and spaces, with at least one dash
        for part in parts:
            if not part.strip():  # Empty part
                continue
            if not re.match(r'^[\-\s]+$', part):  # Not only dashes and spaces
                return False
            if '-' not in part:  # No dashes at all
                return False
        
        return True
    
    def extract_article_numbers(self, lines: List[str]) -> List[Tuple[int, int, str]]:
        """Extract article numbers from lines. Returns list of (line_number, article_number, full_line)"""
        articles = []
        for i, line in enumerate(lines):
            # Match patterns like "### ARTÍCULO 1.-" or "#### ARTÍCULO 54.-"
            match = re.search(r'^#+\s*ARTÍCULO\s+(\d+)\.-', line.strip(), re.IGNORECASE)
            if match:
                article_num = int(match.group(1))
                articles.append((i + 1, article_num, line.strip()))
        return articles
    
    def validate_article_sequence(self, articles: List[Tuple[int, int, str]]) -> Tuple[bool, List[str]]:
        """Validate that main articles (### level) are sequential. Returns (is_valid, issues)"""
        if not articles:
            return True, []
        
        issues = []
        main_articles = []
        reference_articles = []
        
        # Separate main articles (###) from reference articles (#### or #####)
        for line_num, article_num, full_line in articles:
            if full_line.startswith('###'):
                main_articles.append((line_num, article_num, full_line))
            else:
                reference_articles.append((line_num, article_num, full_line))
        
        # Check main articles for sequential numbering (only ### level articles)
        if main_articles:
            expected_num = 1
            for line_num, article_num, full_line in main_articles:
                if article_num != expected_num:
                    issues.append(f"Line {line_num}: Expected main ARTÍCULO {expected_num}, found ARTÍCULO {article_num}")
                expected_num += 1
        
        # Reference articles (#### level) can have any number - they are references within main articles
        # No validation needed for reference articles as they can reference any article number
        
        return len(issues) == 0, issues
    
    def fix_article_sequence(self, lines: List[str]) -> List[str]:
        """Fix article sequence to be correlative"""
        fixed_lines = []
        article_counter = 1
        
        for line in lines:
            # Check if this is a main article line (### level)
            match = re.search(r'^(###\s*ARTÍCULO\s+)\d+(\.-.*)', line.strip(), re.IGNORECASE)
            if match:
                prefix = match.group(1)
                suffix = match.group(2)
                # Replace with sequential number
                new_line = f"{prefix}{article_counter}{suffix}\n"
                fixed_lines.append(new_line)
                article_counter += 1
                self.fixes_applied['article_formatting'] += 1
            else:
                fixed_lines.append(line)
        
        return fixed_lines
    
    def compare_article_numbers_between_steps(self, step5_file: str, step6_file: str) -> bool:
        """Compare article numbers between Step 5 and Step 6 files"""
        print("    Validating article sequence between Step 5 and Step 6...")
        
        # Read both files
        step5_lines = self.read_file(step5_file)
        step6_lines = self.read_file(step6_file)
        
        if not step5_lines or not step6_lines:
            print("    Warning: Could not read step files for validation")
            return False
        
        # Extract articles from both steps
        step5_articles = self.extract_article_numbers(step5_lines)
        step6_articles = self.extract_article_numbers(step6_lines)
        
        # Separate main articles (###) from reference articles (####)
        step5_main = [(ln, an, fl) for ln, an, fl in step5_articles if fl.startswith('###')]
        step5_ref = [(ln, an, fl) for ln, an, fl in step5_articles if fl.startswith('####')]
        step6_main = [(ln, an, fl) for ln, an, fl in step6_articles if fl.startswith('###')]
        step6_ref = [(ln, an, fl) for ln, an, fl in step6_articles if fl.startswith('####')]
        
        print(f"    Step 5: Found {len(step5_main)} main articles (###) and {len(step5_ref)} reference articles (####)")
        print(f"    Step 6: Found {len(step6_main)} main articles (###) and {len(step6_ref)} reference articles (####)")
        
        # Validate Step 5 sequence (only main articles need to be sequential)
        step5_valid, step5_issues = self.validate_article_sequence(step5_articles)
        if not step5_valid:
            print("    Step 5 main article sequence issues:")
            for issue in step5_issues[:5]:  # Show first 5 issues
                print(f"      - {issue}")
            if len(step5_issues) > 5:
                print(f"      ... and {len(step5_issues) - 5} more issues")
        else:
            print("    Step 5: Main articles are correctly sequential ✓")
        
        # Validate Step 6 sequence (only main articles need to be sequential)
        step6_valid, step6_issues = self.validate_article_sequence(step6_articles)
        if not step6_valid:
            print("    Step 6 main article sequence issues:")
            for issue in step6_issues[:5]:  # Show first 5 issues
                print(f"      - {issue}")
            if len(step6_issues) > 5:
                print(f"      ... and {len(step6_issues) - 5} more issues")
        else:
            print("    Step 6: Main articles are correctly sequential ✓")
        
        # Compare article counts
        if len(step5_articles) != len(step6_articles):
            print(f"    WARNING: Total article count changed from Step 5 ({len(step5_articles)}) to Step 6 ({len(step6_articles)})")
        
        if len(step5_main) != len(step6_main):
            print(f"    WARNING: Main article count changed from Step 5 ({len(step5_main)}) to Step 6 ({len(step6_main)})")
        
        # Show first few main articles from each step for comparison
        print("    First 10 main articles (###) in Step 5:")
        for i, (line_num, article_num, full_line) in enumerate(step5_main[:10]):
            print(f"      Line {line_num}: ### ARTÍCULO {article_num}")
        
        print("    First 10 main articles (###) in Step 6:")
        for i, (line_num, article_num, full_line) in enumerate(step6_main[:10]):
            print(f"      Line {line_num}: ### ARTÍCULO {article_num}")
        
        # Show some reference articles as examples (they can have any number)
        if step5_ref:
            print("    Example reference articles (####) in Step 5 (can have any number):")
            for i, (line_num, article_num, full_line) in enumerate(step5_ref[:5]):
                print(f"      Line {line_num}: #### ARTÍCULO {article_num} (reference)")
        
        return step5_valid and step6_valid
    
    def fix_new_requirements(self, lines: List[str]) -> List[str]:
        """Fix issues based on new requirements"""
        fixed_lines = []
        i = 0
        in_disposiciones_relacionadas = False
        in_nota_del_editor = False
        
        while i < len(lines):
            line = lines[i]
            
            if re.search(r'####\s*Disposiciones\s+Relacionadas', line, re.IGNORECASE):
                in_disposiciones_relacionadas = True
                in_nota_del_editor = False
                fixed_lines.append(line)
                i += 1
                continue
            elif re.search(r'####\s*Nota\s+del\s+Editor', line, re.IGNORECASE):
                in_nota_del_editor = True
                in_disposiciones_relacionadas = False
                fixed_lines.append(line)
                i += 1
                continue
            elif re.search(r'^###\s+ARTÍCULO\s+\d+', line, re.IGNORECASE):
                # Check if this is a main article (sequential) or a reference article
                if in_disposiciones_relacionadas or in_nota_del_editor:
                    # This is a reference article, should have 4 hashtags
                    article_content = re.sub(r'^###\s*', '', line.strip())
                    fixed_lines.append(f"#### {article_content}\n")
                    self.fixes_applied['article_hierarchy_fixes'] += 1
                else:
                    # This is a main article, keep 3 hashtags and exit reference sections
                    in_disposiciones_relacionadas = False
                    in_nota_del_editor = False
                    fixed_lines.append(line)
                i += 1
                continue
            elif re.search(r'^##\s+(SECCIÓN|CAPÍTULO|TÍTULO)', line, re.IGNORECASE):
                in_disposiciones_relacionadas = False
                in_nota_del_editor = False
                fixed_lines.append(line)
                i += 1
                continue
            
            # Exit reference sections when we encounter major section headers
            if re.search(r'^(SUJETOS|NACIMIENTO|BASE\s+IMPONIBLE)', line.strip(), re.IGNORECASE):
                in_disposiciones_relacionadas = False
                in_nota_del_editor = False
            
            if re.search(r'##\s*\|\s*DECRETOS\s+SUPREMOS', line, re.IGNORECASE):
                fixed_line = re.sub(r'^##\s*', '', line)
                fixed_lines.append(fixed_line)
                self.fixes_applied['table_hashtag_fixes'] += 1
                i += 1
                continue
            
            if re.search(r"'\s*ARTÍCULO\s+\d+", line, re.IGNORECASE):
                clean_line = re.sub(r"'\s*", '', line)
                
                if in_disposiciones_relacionadas or in_nota_del_editor:
                    if clean_line.strip().startswith('#'):
                        article_content = re.sub(r'^#+\s*', '', clean_line.strip())
                        fixed_lines.append(f"##### {article_content}\n")
                    else:
                        fixed_lines.append(f"##### {clean_line}")
                    self.fixes_applied['article_hierarchy_fixes'] += 1
                else:
                    fixed_lines.append(clean_line)
                
                self.fixes_applied['article_quote_prefix_fixes'] += 1
                i += 1
                continue
            
            if re.search(r'-\s*\'\s*ARTÍCULO\s+\d+', line, re.IGNORECASE):
                if line.strip().startswith('#'):
                    clean_line = re.sub(r'^#+\s*', '', line.strip())
                    fixed_lines.append(f"{clean_line}\n")
                    self.fixes_applied['reference_hashtag_fixes'] += 1
                else:
                    fixed_lines.append(line)
                i += 1
                continue
            
            if line.strip().startswith('#####'):
                is_valid_five_hashtag = False
                
                if (in_disposiciones_relacionadas or in_nota_del_editor) and re.search(r'ARTÍCULO\s+\d+.*\.-', line, re.IGNORECASE):
                    is_valid_five_hashtag = True
                
                if not is_valid_five_hashtag:
                    clean_content = re.sub(r'^#+\s*', '', line.strip())
                    fixed_lines.append(f"{clean_content}\n")
                    self.fixes_applied['incorrect_five_hashtag_fixes'] += 1
                    i += 1
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        return fixed_lines
    
    def is_table_line(self, line: str) -> bool:
        """Check if a line is part of a table structure"""
        return '|' in line and line.strip().count('|') >= 2
    
    def is_in_table_section(self, lines: List[str], current_index: int) -> bool:
        """Check if current line is within a TABLA DE CORRESPONDENCIAS section"""
        # Look backwards for the table section header
        for i in range(current_index - 1, max(0, current_index - 20), -1):
            if re.search(r'TABLA\s+DE\s+CORRESPONDENCIAS', lines[i], re.IGNORECASE):
                # Check if we've hit a new major section since then
                for j in range(i + 1, current_index):
                    if re.search(r'^##\s+(ANEXO|DECRETO|LEY\s+N°|IMPUESTOS\s+NACIONALES|ÍNDICE)', lines[j], re.IGNORECASE):
                        return False
                return True
        return False
    
    def fix_table_and_indice_issues(self, lines: List[str]) -> List[str]:
        """Fix specific issues with tables and completely remove INDICE sections"""
        fixed_lines = []
        in_table_section = False
        in_indice_section = False
        skip_malformed_table = False
        last_was_table_line = False
        pending_table_row = None  # To handle broken table rows
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Detect TABLA DE CORRESPONDENCIAS section
            if re.search(r'TABLA\s+DE\s+CORRESPONDENCIAS', line, re.IGNORECASE):
                in_table_section = True
                in_indice_section = False
                skip_malformed_table = False
                last_was_table_line = False
                pending_table_row = None
                fixed_lines.append(line)
                continue
            
            # FIXED: More specific ÍNDICE detection to avoid removing legitimate content
            # Only detect ÍNDICE if it's a standalone section header, not part of other content
            if (re.search(r'^ÍNDICE\s*$', line.strip(), re.IGNORECASE) and 
                not self.is_table_line(line) and 
                not line.strip().startswith('#')):
                # Look ahead to confirm this is actually an index section
                is_real_indice = False
                for j in range(i + 1, min(i + 10, len(lines))):
                    if (re.search(r'Capítulo\s+[IVX]+', lines[j], re.IGNORECASE) or
                        re.search(r'\.{5,}', lines[j]) or
                        re.search(r'DECRETO\s+SUPREMO', lines[j], re.IGNORECASE)):
                        is_real_indice = True
                        break
                    elif re.search(r'^###?\s+ARTÍCULO\s+\d+', lines[j], re.IGNORECASE):
                        # If we find an article soon after, this is not an index
                        break
                
                if is_real_indice:
                    in_indice_section = True
                    in_table_section = False
                    skip_malformed_table = False
                    last_was_table_line = False
                    # Skip this line and everything in the ÍNDICE section
                    continue
            
            # Detect malformed table content that looks like INDICE remnants
            # These are lines that have table-like structure but contain chapter/page info
            if (re.search(r'##\s*\|\s*Capítulo\s+[IVX]+\s*\|', line, re.IGNORECASE) or
                re.search(r'\|\s*Disposiciones\s+.*\.{5,}.*\d+\s*\|', line, re.IGNORECASE) or
                re.search(r'\|\s*DECRETO\s+SUPREMO.*\.{5,}.*\d+\s*\|', line, re.IGNORECASE) or
                re.search(r'\|\s*ANEXO.*\.{5,}.*\d+\s*\|', line, re.IGNORECASE) or
                re.search(r'\|\s*Cálculo\s+de\s+la\s+Deuda.*\|', line, re.IGNORECASE) or
                re.search(r'\|\s*REGLAMENT.*CÓDIGO.*TRIBUTARIO.*\|', line, re.IGNORECASE)):
                skip_malformed_table = True
                last_was_table_line = False
                continue
            
            # Skip malformed table lines that are part of INDICE remnants
            if skip_malformed_table:
                # Check if this line is still part of the malformed table
                if (self.is_table_line(line) or 
                    re.search(r'^\s*\|\s*.*\s*\|\s*$', line) or
                    re.search(r'Capítulo\s+[IVX]+', line, re.IGNORECASE) or
                    re.search(r'\.{5,}', line) or
                    re.search(r'DECRETO\s+SUPREMO', line, re.IGNORECASE) or
                    re.search(r'REGLAMENT', line, re.IGNORECASE)):
                    continue
                else:
                    # We've moved past the malformed table
                    skip_malformed_table = False
            
            # NEW: Remove stray "Central" text that appears after table lines
            # This handles the specific issue mentioned in the task
            if (last_was_table_line and 
                line.strip() == 'Central' and 
                not self.is_table_line(line)):
                # Skip this "Central" line - it's unwanted text between table and next section
                self.fixes_applied['table_hashtag_fixes'] += 1
                last_was_table_line = False
                continue
            
            # Exit table section when we encounter a new major section
            if in_table_section and re.search(r'^##\s+(ANEXO|DECRETO|LEY\s+N°|IMPUESTOS\s+NACIONALES)', line, re.IGNORECASE):
                in_table_section = False
                last_was_table_line = False
            
            # FIXED: More conservative INDICE section exit logic
            if in_indice_section:
                # Look for major section headers that would end the INDICE
                # Be more specific about what ends an INDICE section
                if (re.search(r'^##\s+(IMPUESTOS\s+NACIONALES|TÍTULO\s+[IVX]+|LEY\s+N°|CAPÍTULO|SECCIÓN)', line, re.IGNORECASE) or
                    re.search(r'^###\s+ARTÍCULO\s+\d+', line, re.IGNORECASE) or
                    re.search(r'^OBJETO\s*$', line.strip(), re.IGNORECASE) or
                    re.search(r'^SUJETOS\s*$', line.strip(), re.IGNORECASE)):
                    in_indice_section = False
                    last_was_table_line = False
                    # Don't continue here - process this line normally
                else:
                    # Still in INDICE section, skip this line
                    continue
            
            # Skip everything in ÍNDICE section (this check is now redundant but kept for safety)
            if in_indice_section:
                continue
            
            # FIX 2: Handle table formatting issues in TABLA DE CORRESPONDENCIAS section
            if in_table_section:
                # In table sections, preserve all lines exactly as they are
                # Don't try to combine or modify table rows as this causes scrambling
                fixed_lines.append(original_line)
                last_was_table_line = self.is_table_line(line)
                continue
            
            # Track if current line is a table line for next iteration
            current_is_table_line = self.is_table_line(line)
            
            fixed_lines.append(line)
            last_was_table_line = current_is_table_line
        
        return fixed_lines
    
    def apply_simple_cleaning(self, lines: List[str]) -> List[str]:
        """Apply simple cleaning - only remove specific unwanted patterns while preserving formatting"""
        fixed_lines = []
        
        # Remove only these two specific patterns line by line to preserve formatting
        unwanted_patterns = [
            r"<!-- image -->",  # Remove image placeholders from markdown
            r"Prohibida su reproducción impresa o digital sin autorización",
        ]
        
        for line in lines:
            original_line = line
            
            # Apply pattern removal to each line
            for pattern in unwanted_patterns:
                line = re.sub(pattern, "", line, flags=re.IGNORECASE)
            
            # Only count as a fix if the line actually changed
            if line != original_line:
                self.fixes_applied['strange_characters'] += 1
            
            fixed_lines.append(line)
        
        return fixed_lines

    def classify_content_type(self, line: str) -> str:
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

    def classify_detailed_content_type(self, line: str) -> str:
        """Classify content with more detailed categories"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return 'empty'
        
        # Title patterns (major sections)
        title_patterns = [
            r'^#+\s+LEY\s+N°',
            r'^#+\s+CÓDIGO\s+TRIBUTARIO',
            r'^#+\s+CAPÍTULO',
            r'^#+\s+SECCIÓN',
            r'^#+\s+TÍTULO',
            r'^#+\s+ANEXO',
            r'^#+\s+Presentación',
        ]
        
        # Subtitle patterns (articles and subsections)
        subtitle_patterns = [
            r'^#+\s+ARTÍCULO\s+\d+',
            r'^#+\s+Disposiciones\s+Relacionadas',
            r'^#+\s+Nota\s+del\s+Editor',
            r'^#+\s+DECRETOS?\s+SUPREMOS?',
            r'^#+\s+IMPUESTOS\s+NACIONALES',
        ]
        
        # List item patterns
        list_patterns = [
            r'^\d+\.\s+',  # Numbered lists: "1. ", "2. ", etc.
            r'^[a-z]\)\s+',  # Letter lists: "a) ", "b) ", etc.
            r'^[IVX]+\.\s+',  # Roman numeral lists: "I. ", "II. ", etc.
            r'^-\s+[IVX]+\.',  # Roman with dash: "- I.", "- II.", etc.
        ]
        
        # Check for titles
        for pattern in title_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return 'title'
        
        # Check for subtitles
        for pattern in subtitle_patterns:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return 'subtitle'
        
        # Check for list items
        for pattern in list_patterns:
            if re.search(pattern, line_stripped):
                return 'list_item'
        
        # Default to paragraph if it has content
        if line_stripped:
            return 'paragraph'
        
        return 'empty'

    def fix_newlines_batch_processing(self, lines: List[str]) -> List[str]:
        """Apply batch-based intelligent newline processing with refined rules that preserve table formatting"""
        fixed_lines = []
        i = 0
        in_table_section = False
        
        while i < len(lines):
            line = lines[i]
            
            # Check if we're in a table section
            if re.search(r'TABLA\s+DE\s+CORRESPONDENCIAS', line, re.IGNORECASE):
                in_table_section = True
            elif re.search(r'^##\s+(ANEXO|DECRETO|LEY\s+N°|IMPUESTOS\s+NACIONALES)', line, re.IGNORECASE):
                in_table_section = False
            
            # If we're in a table section, preserve the original formatting
            if in_table_section:
                # Preserve original line exactly as is
                fixed_lines.append(line)
                i += 1
                continue
            
            # For non-table sections, apply minimal processing
            content_type = self.classify_detailed_content_type(line)
            
            if content_type == 'empty':
                # Skip empty lines but preserve one empty line between different content types
                if (i > 0 and i < len(lines) - 1 and 
                    lines[i-1].strip() and lines[i+1].strip()):
                    # Look ahead to see if next non-empty line is different type
                    next_line_type = self.classify_detailed_content_type(lines[i+1])
                    prev_line_type = self.classify_detailed_content_type(lines[i-1])
                    
                    # Preserve empty line between different content types
                    if (next_line_type in ['title', 'subtitle'] or 
                        prev_line_type in ['title', 'subtitle']):
                        fixed_lines.append('\n')
                
                i += 1
                continue
            else:
                # Add content line with newline
                if line.endswith('\n'):
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line + '\n')
                i += 1
                continue
        
        return fixed_lines

    def apply_markdown_fixes(self, file_path: str) -> bool:
        """Apply all markdown fixes to the file with temporal file generation"""
        print(f"Applying markdown fixes to: {file_path}")
        
        lines = self.read_file(file_path)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Create temp directory inside output/
        temp_dir = "output/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate base filename for temporal files
        base_filename = self.generate_filename_from_path(file_path)
        
        # Step 0: Save original file before any cleanup
        print("  0. Saving original file...")
        temp_file_0 = os.path.join(temp_dir, f"temp_00_original_{base_filename}.md")
        self.write_file(lines, temp_file_0)
        print(f"     Original file saved: {temp_file_0}")
        
        # Apply fixes in order with temporal file generation
        print("Applying fixes...")
        
        # Step 1: Simple cleaning - only remove specific patterns
        print("  1. Applying simple cleaning...")
        lines = self.apply_simple_cleaning(lines)
        temp_file_1 = os.path.join(temp_dir, f"temp_01_simple_cleaning_{base_filename}.md")
        self.write_file(lines, temp_file_1)
        print(f"     Temporal file saved: {temp_file_1}")
        
        # Step 2: Remove empty hashtags
        print("  2. Removing empty hashtags...")
        lines = self.fix_empty_hashtags(lines)
        temp_file_2 = os.path.join(temp_dir, f"temp_02_empty_hashtags_{base_filename}.md")
        self.write_file(lines, temp_file_2)
        print(f"     Temporal file saved: {temp_file_2}")
        
        # Step 3: Remove dash separators
        print("  3. Removing dash separators...")
        lines = self.fix_dash_separators(lines)
        temp_file_3 = os.path.join(temp_dir, f"temp_03_dash_separators_{base_filename}.md")
        self.write_file(lines, temp_file_3)
        print(f"     Temporal file saved: {temp_file_3}")
        
        # Step 4: Fix header hierarchy
        print("  4. Fixing header hierarchy...")
        lines = self.fix_header_hierarchy(lines)
        temp_file_4 = os.path.join(temp_dir, f"temp_04_header_hierarchy_{base_filename}.md")
        self.write_file(lines, temp_file_4)
        print(f"     Temporal file saved: {temp_file_4}")
        
        # Step 5: Fix new requirements
        print("  5. Fixing new requirements...")
        lines = self.fix_new_requirements(lines)
        temp_file_5 = os.path.join(temp_dir, f"temp_05_new_requirements_{base_filename}.md")
        self.write_file(lines, temp_file_5)
        print(f"     Temporal file saved: {temp_file_5}")
        
        # Step 6: Fix table and INDICE issues (NEW STEP)
        print("  6. Fixing table and INDICE issues...")
        lines = self.fix_table_and_indice_issues(lines)
        temp_file_6 = os.path.join(temp_dir, f"temp_06_table_indice_{base_filename}.md")
        self.write_file(lines, temp_file_6)
        print(f"     Temporal file saved: {temp_file_6}")
        
        # VALIDATION: Compare article numbers between Step 5 and Step 6
        print("\n  VALIDATION: Checking article sequence between Step 5 and Step 6...")
        validation_result = self.compare_article_numbers_between_steps(temp_file_5, temp_file_6)
        if not validation_result:
            print("    WARNING: Article sequence validation failed!")
            print("    Consider reviewing the article numbering in the output files.")
        else:
            print("    ✓ Article sequence validation passed!")
        
        # Step 7: Fix scattered letters
        print("  7. Fixing scattered letters...")
        lines = self.fix_scattered_letters(lines)
        temp_file_7 = os.path.join(temp_dir, f"temp_07_scattered_letters_{base_filename}.md")
        self.write_file(lines, temp_file_7)
        print(f"     Temporal file saved: {temp_file_7}")
        
        # Step 8: Fix strange characters
        print("  8. Fixing strange characters...")
        lines = self.fix_strange_characters(lines)
        temp_file_8 = os.path.join(temp_dir, f"temp_08_strange_characters_{base_filename}.md")
        self.write_file(lines, temp_file_8)
        print(f"     Temporal file saved: {temp_file_8}")
        
        # Step 9: Apply batch newline processing
        print("  9. Applying batch newline processing...")
        lines = self.fix_newlines_batch_processing(lines)
        temp_file_9 = os.path.join(temp_dir, f"temp_09_batch_newlines_{base_filename}.md")
        self.write_file(lines, temp_file_9)
        print(f"     Temporal file saved: {temp_file_9}")
        
        # Step 10: Fix excessive whitespace (final step)
        print("  10. Fixing excessive whitespace...")
        lines = self.fix_excessive_whitespace(lines)
        temp_file_10 = os.path.join(temp_dir, f"temp_10_excessive_whitespace_{base_filename}.md")
        self.write_file(lines, temp_file_10)
        print(f"     Temporal file saved: {temp_file_10}")
        
        print(f"Fixed file has {len(lines)} lines")
        
        # Determine output file
        if self.output_file is None:
            base_name = os.path.splitext(file_path)[0]
            self.output_file = f"{base_name}_processed.md"
        
        self.write_file(lines, self.output_file)
        
        # Print summary
        print("\nFixes applied:")
        for fix_type, count in self.fixes_applied.items():
            if count > 0:
                print(f"  - {fix_type}: {count}")
        
        total_fixes = sum(self.fixes_applied.values())
        print(f"\nTotal fixes applied: {total_fixes}")
        
        print(f"\nTemporal files generated:")
        print(f"  - {temp_file_1}")
        print(f"  - {temp_file_2}")
        print(f"  - {temp_file_3}")
        print(f"  - {temp_file_4}")
        print(f"  - {temp_file_5}")
        print(f"  - {temp_file_6}")
        print(f"  - {temp_file_7}")
        print(f"  - {temp_file_8}")
        print(f"  - {temp_file_9}")
        print(f"  - {temp_file_10}")
        
        return True
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_md_file and os.path.exists(self.temp_md_file):
            try:
                os.remove(self.temp_md_file)
                print(f"Cleaned up temporary file: {self.temp_md_file}")
            except Exception as e:
                print(f"Warning: Could not remove temporary file {self.temp_md_file}: {e}")
    
    def process(self) -> bool:
        """Main processing workflow"""
        print("=" * 60)
        print("PDF TO MARKDOWN PROCESSING PIPELINE")
        print("=" * 60)
        print(f"Input file: {self.input_file}")
        print(f"Output file: {self.output_file or 'Auto-generated'}")
        print()
        
        try:
            # Step 1: Handle PDF extraction if needed
            if self.is_pdf_file(self.input_file):
                print("Step 1: Extracting markdown from PDF...")
                md_file = self.extract_markdown_from_pdf()
                if not md_file:
                    print("Error: Failed to extract markdown from PDF")
                    return False
                processing_file = md_file
            else:
                print("Step 1: Input is already a markdown file, skipping PDF extraction...")
                processing_file = self.input_file
            
            # Step 2: Analyze markdown for issues
            print("\nStep 2: Analyzing markdown for issues...")
            results = self.analyze_markdown_issues(processing_file)
            total_issues = sum(len(result.issues) for result in results)
            print(f"Analysis complete: {total_issues} issues found")
            
            # Step 3: Apply comprehensive fixes
            print("\nStep 3: Applying comprehensive fixes...")
            success = self.apply_markdown_fixes(processing_file)
            
            if not success:
                print("Error: Failed to apply fixes")
                return False
            
            # Step 4: Final verification
            print("\nStep 4: Verifying results...")
            final_results = self.analyze_markdown_issues(self.output_file)
            final_issues = sum(len(result.issues) for result in final_results)
            issues_resolved = total_issues - final_issues
            
            print("\n" + "=" * 60)
            print("PROCESSING COMPLETE")
            print("=" * 60)
            print(f"Original issues: {total_issues}")
            print(f"Remaining issues: {final_issues}")
            print(f"Issues resolved: {issues_resolved}")
            if total_issues > 0:
                print(f"Success rate: {(issues_resolved/total_issues)*100:.1f}%")
            else:
                print("Success rate: 100.0% (no issues found)")
            print(f"\nFinal document: {self.output_file}")
            
            return True
            
        except Exception as e:
            print(f"Error during processing: {e}")
            return False
        
        finally:
            # Clean up temporary files
            self.cleanup_temp_files()


def main():
    """Main function to run the PDF to Markdown processor"""
    parser = argparse.ArgumentParser(
        description='Complete PDF to Markdown Processing Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pdf_to_markdown_processor.py document.pdf
  python pdf_to_markdown_processor.py document.pdf --output final_document.md
  python pdf_to_markdown_processor.py document.md --output cleaned_document.md
        """
    )
    
    parser.add_argument('input_file', help='Input PDF or markdown file to process')
    parser.add_argument('--output', '-o', help='Output markdown file path (default: auto-generated)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Check file extension
    if not (args.input_file.lower().endswith('.pdf') or args.input_file.lower().endswith('.md')):
        print("Error: Input file must be a PDF (.pdf) or Markdown (.md) file")
        sys.exit(1)
    
    # Create processor and run
    processor = PDFToMarkdownProcessor(args.input_file, args.output)
    success = processor.process()
    
    if success:
        print("\n✅ Processing completed successfully!")
        if processor.output_file:
            print(f"📄 Final processed file: {processor.output_file}")
    else:
        print("\n❌ Processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
