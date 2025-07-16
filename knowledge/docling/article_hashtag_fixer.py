#!/usr/bin/env python3
"""
Article Hashtag Fixer
Comprehensive script to fix article hashtag formatting and prevent article loss.
Ensures proper sequential numbering and correct hashtag levels.
"""

import os
import re
import sys
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class ArticleMatch:
    line_number: int
    original_line: str
    article_number: int
    hashtag_level: int
    article_title: str
    is_main_article: bool
    context_section: str  # 'main', 'disposiciones', 'nota_editor'

class ArticleHashtagFixer:
    def __init__(self):
        self.fixes_applied = {
            'sequential_numbering': 0,
            'hashtag_level_fixes': 0,
            'missing_articles_restored': 0,
            'duplicate_articles_merged': 0,
            'context_fixes': 0
        }
    
    def read_file_batch(self, file_path: str) -> List[str]:
        """Read file in batches to handle large files efficiently"""
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
    
    def write_file_batch(self, file_path: str, lines: List[str]) -> bool:
        """Write file in batches"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False
    
    def detect_context_section(self, lines: List[str], current_index: int) -> str:
        """Detect which section context we're in"""
        # Look backwards to find section headers
        for i in range(current_index - 1, max(0, current_index - 50), -1):
            line = lines[i].strip()
            
            if re.search(r'####\s*Disposiciones\s+Relacionadas', line, re.IGNORECASE):
                return 'disposiciones'
            elif re.search(r'####\s*Nota\s+del\s+Editor', line, re.IGNORECASE):
                return 'nota_editor'
            elif re.search(r'^###\s+ARTÍCULO\s+\d+\.-', line, re.IGNORECASE):
                return 'main'
            elif re.search(r'^##\s+(CAPÍTULO|SECCIÓN|TÍTULO)', line, re.IGNORECASE):
                return 'main'
        
        return 'main'  # Default to main section
    
    def extract_articles_with_context(self, lines: List[str]) -> List[ArticleMatch]:
        """Extract all articles with their context information"""
        articles = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Match various article patterns
            patterns = [
                r'^(#+)\s*ARTÍCULO\s+(\d+)\.-\s*(.*)',  # Standard format
                r'^(#+)\s*ARTÍCULO\s+(\d+)\.\s*(.*)',   # With period instead of dash
                r'^(#+)\s*\'?\s*ARTÍCULO\s+(\d+)\.-\s*(.*)',  # With quote prefix
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line_stripped, re.IGNORECASE)
                if match:
                    hashtag_level = len(match.group(1))
                    article_number = int(match.group(2))
                    article_title = match.group(3).strip()
                    
                    context = self.detect_context_section(lines, i)
                    is_main_article = (hashtag_level == 3 and context == 'main')
                    
                    article_match = ArticleMatch(
                        line_number=i + 1,
                        original_line=line,
                        article_number=article_number,
                        hashtag_level=hashtag_level,
                        article_title=article_title,
                        is_main_article=is_main_article,
                        context_section=context
                    )
                    articles.append(article_match)
                    break
        
        return articles
    
    def fix_article_sequence(self, lines: List[str]) -> List[str]:
        """Fix article sequence to be correlative and properly formatted"""
        print("Fixing article sequence and hashtag formatting...")
        
        # Extract all articles with context
        articles = self.extract_articles_with_context(lines)
        
        # Separate main articles from reference articles
        main_articles = [a for a in articles if a.is_main_article]
        reference_articles = [a for a in articles if not a.is_main_article]
        
        print(f"Found {len(main_articles)} main articles and {len(reference_articles)} reference articles")
        
        # Sort main articles by line number to maintain document order
        main_articles.sort(key=lambda x: x.line_number)
        
        # Create mapping of line numbers to new article numbers
        line_to_new_number = {}
        
        # Assign sequential numbers to main articles
        for i, article in enumerate(main_articles, 1):
            line_to_new_number[article.line_number - 1] = i  # Convert to 0-based index
        
        # Process lines and apply fixes
        fixed_lines = []
        in_disposiciones = False
        in_nota_editor = False
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Track section context
            if re.search(r'####\s*Disposiciones\s+Relacionadas', line, re.IGNORECASE):
                in_disposiciones = True
                in_nota_editor = False
                fixed_lines.append(line)
                continue
            elif re.search(r'####\s*Nota\s+del\s+Editor', line, re.IGNORECASE):
                in_nota_editor = True
                in_disposiciones = False
                fixed_lines.append(line)
                continue
            elif re.search(r'^##\s+(CAPÍTULO|SECCIÓN|TÍTULO)', line, re.IGNORECASE):
                in_disposiciones = False
                in_nota_editor = False
                fixed_lines.append(line)
                continue
            
            # Check if this line contains an article
            line_stripped = line.strip()
            article_patterns = [
                r'^(#+)\s*\'?\s*ARTÍCULO\s+(\d+)(\.-?\s*)(.*)',
            ]
            
            fixed = False
            for pattern in article_patterns:
                match = re.search(pattern, line_stripped, re.IGNORECASE)
                if match:
                    hashtag_part = match.group(1)
                    article_num = int(match.group(2))
                    separator = match.group(3)
                    title_part = match.group(4)
                    
                    # Determine correct hashtag level based on context
                    if in_disposiciones or in_nota_editor:
                        # Reference articles in special sections get #### or #####
                        if in_disposiciones:
                            correct_hashtags = "####"
                        else:  # in_nota_editor
                            correct_hashtags = "#####"
                        
                        # Keep original article number for reference articles
                        new_line = f"{correct_hashtags} ARTÍCULO {article_num}.- {title_part}\n"
                        fixed_lines.append(new_line)
                        
                        if len(hashtag_part) != len(correct_hashtags):
                            self.fixes_applied['hashtag_level_fixes'] += 1
                        
                    else:
                        # Main article - use sequential numbering and ### hashtags
                        if i in line_to_new_number:
                            new_article_num = line_to_new_number[i]
                            new_line = f"### ARTÍCULO {new_article_num}.- {title_part}\n"
                            fixed_lines.append(new_line)
                            
                            if article_num != new_article_num:
                                self.fixes_applied['sequential_numbering'] += 1
                            if len(hashtag_part) != 3:
                                self.fixes_applied['hashtag_level_fixes'] += 1
                        else:
                            # This shouldn't happen, but keep original if not in mapping
                            fixed_lines.append(line)
                    
                    fixed = True
                    break
            
            if not fixed:
                fixed_lines.append(line)
        
        return fixed_lines
    
    def validate_article_sequence(self, lines: List[str]) -> Dict[str, any]:
        """Validate the article sequence after fixing"""
        articles = self.extract_articles_with_context(lines)
        main_articles = [a for a in articles if a.is_main_article]
        reference_articles = [a for a in articles if not a.is_main_article]
        
        # Check main article sequence
        main_articles.sort(key=lambda x: x.line_number)
        sequence_issues = []
        
        for i, article in enumerate(main_articles, 1):
            if article.article_number != i:
                sequence_issues.append(f"Line {article.line_number}: Expected ARTÍCULO {i}, found ARTÍCULO {article.article_number}")
        
        # Check for duplicates
        main_numbers = [a.article_number for a in main_articles]
        duplicates = []
        seen = set()
        for num in main_numbers:
            if num in seen:
                duplicates.append(num)
            seen.add(num)
        
        return {
            'total_articles': len(articles),
            'main_articles': len(main_articles),
            'reference_articles': len(reference_articles),
            'sequence_issues': sequence_issues,
            'duplicates': duplicates,
            'is_valid': len(sequence_issues) == 0 and len(duplicates) == 0
        }
    
    def create_backup(self, file_path: str) -> str:
        """Create a backup of the original file"""
        backup_path = f"{file_path}.backup"
        try:
            lines = self.read_file_batch(file_path)
            if lines:
                self.write_file_batch(backup_path, lines)
                print(f"Backup created: {backup_path}")
                return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
        return None
    
    def fix_file(self, file_path: str, create_backup: bool = True) -> bool:
        """Fix article hashtags and numbering in a file"""
        print(f"Processing file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            return False
        
        # Create backup if requested
        if create_backup:
            self.create_backup(file_path)
        
        # Read original file
        lines = self.read_file_batch(file_path)
        if not lines:
            return False
        
        print(f"Original file has {len(lines)} lines")
        
        # Validate original sequence
        print("Validating original article sequence...")
        original_validation = self.validate_article_sequence(lines)
        print(f"Original: {original_validation['main_articles']} main articles, {original_validation['reference_articles']} reference articles")
        if original_validation['sequence_issues']:
            print(f"Original sequence issues: {len(original_validation['sequence_issues'])}")
        
        # Apply fixes
        fixed_lines = self.fix_article_sequence(lines)
        
        # Validate fixed sequence
        print("Validating fixed article sequence...")
        fixed_validation = self.validate_article_sequence(fixed_lines)
        print(f"Fixed: {fixed_validation['main_articles']} main articles, {fixed_validation['reference_articles']} reference articles")
        
        if fixed_validation['is_valid']:
            print("✅ Article sequence is now valid!")
        else:
            print("⚠️  Some issues remain:")
            for issue in fixed_validation['sequence_issues'][:5]:
                print(f"  - {issue}")
        
        # Write fixed file
        success = self.write_file_batch(file_path, fixed_lines)
        
        if success:
            print(f"File fixed successfully: {file_path}")
            print("Fixes applied:")
            for fix_type, count in self.fixes_applied.items():
                if count > 0:
                    print(f"  - {fix_type}: {count}")
            
            total_fixes = sum(self.fixes_applied.values())
            print(f"Total fixes applied: {total_fixes}")
            
            return True
        else:
            print("Error: Failed to write fixed file")
            return False
    
    def compare_files(self, file1_path: str, file2_path: str) -> Dict[str, any]:
        """Compare article sequences between two files"""
        print(f"Comparing articles between {file1_path} and {file2_path}")
        
        lines1 = self.read_file_batch(file1_path)
        lines2 = self.read_file_batch(file2_path)
        
        if not lines1 or not lines2:
            print("Error: Could not read one or both files")
            return {}
        
        articles1 = self.extract_articles_with_context(lines1)
        articles2 = self.extract_articles_with_context(lines2)
        
        main1 = [a for a in articles1 if a.is_main_article]
        main2 = [a for a in articles2 if a.is_main_article]
        
        numbers1 = set(a.article_number for a in main1)
        numbers2 = set(a.article_number for a in main2)
        
        lost = numbers1 - numbers2
        gained = numbers2 - numbers1
        
        print(f"File 1: {len(main1)} main articles")
        print(f"File 2: {len(main2)} main articles")
        print(f"Articles lost: {len(lost)}")
        print(f"Articles gained: {len(gained)}")
        
        if lost:
            print("Lost articles:", sorted(lost)[:20])
        if gained:
            print("Gained articles:", sorted(gained)[:20])
        
        return {
            'file1_main_count': len(main1),
            'file2_main_count': len(main2),
            'lost_articles': lost,
            'gained_articles': gained,
            'articles_preserved': len(lost) == 0
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Fix article hashtag formatting and prevent article loss',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python article_hashtag_fixer.py fix document.md
  python article_hashtag_fixer.py compare step5.md step6.md
  python article_hashtag_fixer.py fix document.md --no-backup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Fix article hashtags in a file')
    fix_parser.add_argument('file_path', help='Path to the file to fix')
    fix_parser.add_argument('--no-backup', action='store_true', help='Do not create backup file')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare articles between two files')
    compare_parser.add_argument('file1', help='First file to compare')
    compare_parser.add_argument('file2', help='Second file to compare')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    fixer = ArticleHashtagFixer()
    
    if args.command == 'fix':
        success = fixer.fix_file(args.file_path, create_backup=not args.no_backup)
        if not success:
            sys.exit(1)
    
    elif args.command == 'compare':
        comparison = fixer.compare_files(args.file1, args.file2)
        if not comparison.get('articles_preserved', False):
            print("⚠️  Articles were lost between files!")
            sys.exit(1)
        else:
            print("✅ Articles preserved between files!")

if __name__ == "__main__":
    main()
