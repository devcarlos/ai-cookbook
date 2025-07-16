#!/usr/bin/env python3
"""
Article Sequence Analyzer
Analyzes article numbering issues between processing steps using batch approach.
Identifies missing articles and sequence problems without reading complete files.
"""

import os
import re
import sys
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass

@dataclass
class ArticleInfo:
    line_number: int
    article_number: int
    hashtag_level: int
    full_line: str
    is_main_article: bool  # True for ### level, False for #### level

class ArticleSequenceAnalyzer:
    def __init__(self):
        self.batch_size = 100  # Process files in batches of 100 lines
        
    def extract_articles_batch(self, file_path: str) -> List[ArticleInfo]:
        """Extract article information using batch processing"""
        articles = []
        
        if not os.path.exists(file_path):
            print(f"Warning: File not found: {file_path}")
            return articles
        
        print(f"Analyzing articles in: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_number = 0
                batch_lines = []
                
                while True:
                    # Read batch of lines
                    batch_lines = []
                    for _ in range(self.batch_size):
                        line = f.readline()
                        if not line:
                            break
                        batch_lines.append(line)
                        line_number += 1
                    
                    if not batch_lines:
                        break
                    
                    # Process batch for articles
                    batch_articles = self.process_batch_for_articles(batch_lines, line_number - len(batch_lines) + 1)
                    articles.extend(batch_articles)
                    
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return []
        
        print(f"Found {len(articles)} articles in {file_path}")
        return articles
    
    def process_batch_for_articles(self, lines: List[str], start_line_number: int) -> List[ArticleInfo]:
        """Process a batch of lines to find articles"""
        articles = []
        
        for i, line in enumerate(lines):
            line_number = start_line_number + i
            line_stripped = line.strip()
            
            # Match article patterns: ### ARTÍCULO X.- or #### ARTÍCULO X.-
            match = re.search(r'^(#+)\s*ARTÍCULO\s+(\d+)\.-', line_stripped, re.IGNORECASE)
            if match:
                hashtag_level = len(match.group(1))
                article_number = int(match.group(2))
                is_main_article = hashtag_level == 3  # ### level articles are main articles
                
                article_info = ArticleInfo(
                    line_number=line_number,
                    article_number=article_number,
                    hashtag_level=hashtag_level,
                    full_line=line_stripped,
                    is_main_article=is_main_article
                )
                articles.append(article_info)
        
        return articles
    
    def analyze_sequence_issues(self, articles: List[ArticleInfo]) -> Dict[str, List[str]]:
        """Analyze sequence issues in articles"""
        issues = {
            'main_sequence_issues': [],
            'missing_articles': [],
            'duplicate_articles': [],
            'reference_articles': []
        }
        
        # Separate main articles (###) from reference articles (####)
        main_articles = [a for a in articles if a.is_main_article]
        reference_articles = [a for a in articles if not a.is_main_article]
        
        # Analyze main article sequence
        if main_articles:
            main_articles.sort(key=lambda x: x.line_number)  # Sort by line number
            expected_num = 1
            seen_numbers = set()
            
            for article in main_articles:
                # Check for duplicates
                if article.article_number in seen_numbers:
                    issues['duplicate_articles'].append(
                        f"Line {article.line_number}: Duplicate main ARTÍCULO {article.article_number}"
                    )
                seen_numbers.add(article.article_number)
                
                # Check sequence
                if article.article_number != expected_num:
                    issues['main_sequence_issues'].append(
                        f"Line {article.line_number}: Expected main ARTÍCULO {expected_num}, found ARTÍCULO {article.article_number}"
                    )
                expected_num += 1
            
            # Check for missing articles in sequence
            all_main_numbers = sorted([a.article_number for a in main_articles])
            if all_main_numbers:
                for i in range(1, max(all_main_numbers) + 1):
                    if i not in all_main_numbers:
                        issues['missing_articles'].append(f"Missing main ARTÍCULO {i}")
        
        # Record reference articles (these can have any number)
        for article in reference_articles:
            issues['reference_articles'].append(
                f"Line {article.line_number}: Reference ARTÍCULO {article.article_number} (#### level)"
            )
        
        return issues
    
    def compare_steps(self, step5_file: str, step6_file: str) -> Dict[str, any]:
        """Compare articles between two processing steps"""
        print("=" * 60)
        print("ARTICLE SEQUENCE COMPARISON")
        print("=" * 60)
        
        # Extract articles from both files
        step5_articles = self.extract_articles_batch(step5_file)
        step6_articles = self.extract_articles_batch(step6_file)
        
        # Analyze each step
        step5_issues = self.analyze_sequence_issues(step5_articles)
        step6_issues = self.analyze_sequence_issues(step6_articles)
        
        # Separate main and reference articles
        step5_main = [a for a in step5_articles if a.is_main_article]
        step5_ref = [a for a in step5_articles if not a.is_main_article]
        step6_main = [a for a in step6_articles if a.is_main_article]
        step6_ref = [a for a in step6_articles if not a.is_main_article]
        
        # Print comparison results
        print(f"\nSTEP 5 ANALYSIS:")
        print(f"  Total articles: {len(step5_articles)}")
        print(f"  Main articles (###): {len(step5_main)}")
        print(f"  Reference articles (####): {len(step5_ref)}")
        
        print(f"\nSTEP 6 ANALYSIS:")
        print(f"  Total articles: {len(step6_articles)}")
        print(f"  Main articles (###): {len(step6_main)}")
        print(f"  Reference articles (####): {len(step6_ref)}")
        
        # Show article count changes
        main_diff = len(step6_main) - len(step5_main)
        ref_diff = len(step6_ref) - len(step5_ref)
        total_diff = len(step6_articles) - len(step5_articles)
        
        print(f"\nCHANGES FROM STEP 5 TO STEP 6:")
        print(f"  Main articles change: {main_diff:+d}")
        print(f"  Reference articles change: {ref_diff:+d}")
        print(f"  Total articles change: {total_diff:+d}")
        
        # Show sequence issues
        if step5_issues['main_sequence_issues']:
            print(f"\nSTEP 5 SEQUENCE ISSUES ({len(step5_issues['main_sequence_issues'])} total):")
            for issue in step5_issues['main_sequence_issues'][:10]:  # Show first 10
                print(f"  - {issue}")
            if len(step5_issues['main_sequence_issues']) > 10:
                print(f"  ... and {len(step5_issues['main_sequence_issues']) - 10} more issues")
        
        if step6_issues['main_sequence_issues']:
            print(f"\nSTEP 6 SEQUENCE ISSUES ({len(step6_issues['main_sequence_issues'])} total):")
            for issue in step6_issues['main_sequence_issues'][:10]:  # Show first 10
                print(f"  - {issue}")
            if len(step6_issues['main_sequence_issues']) > 10:
                print(f"  ... and {len(step6_issues['main_sequence_issues']) - 10} more issues")
        
        # Find specific articles that were lost
        step5_main_numbers = set(a.article_number for a in step5_main)
        step6_main_numbers = set(a.article_number for a in step6_main)
        
        lost_articles = step5_main_numbers - step6_main_numbers
        new_articles = step6_main_numbers - step5_main_numbers
        
        if lost_articles:
            print(f"\nARTICLES LOST FROM STEP 5 TO STEP 6 ({len(lost_articles)} total):")
            for article_num in sorted(lost_articles)[:20]:  # Show first 20
                # Find the line number in step 5
                step5_article = next((a for a in step5_main if a.article_number == article_num), None)
                if step5_article:
                    print(f"  - ARTÍCULO {article_num} (was on line {step5_article.line_number} in Step 5)")
            if len(lost_articles) > 20:
                print(f"  ... and {len(lost_articles) - 20} more lost articles")
        
        if new_articles:
            print(f"\nNEW ARTICLES IN STEP 6 ({len(new_articles)} total):")
            for article_num in sorted(new_articles)[:20]:  # Show first 20
                step6_article = next((a for a in step6_main if a.article_number == article_num), None)
                if step6_article:
                    print(f"  - ARTÍCULO {article_num} (on line {step6_article.line_number} in Step 6)")
            if len(new_articles) > 20:
                print(f"  ... and {len(new_articles) - 20} more new articles")
        
        # Return detailed comparison data
        return {
            'step5_articles': step5_articles,
            'step6_articles': step6_articles,
            'step5_issues': step5_issues,
            'step6_issues': step6_issues,
            'lost_articles': lost_articles,
            'new_articles': new_articles,
            'main_diff': main_diff,
            'ref_diff': ref_diff,
            'total_diff': total_diff
        }
    
    def find_problematic_lines(self, file_path: str, target_lines: List[int]) -> Dict[int, str]:
        """Find specific lines in a file using batch processing"""
        found_lines = {}
        
        if not os.path.exists(file_path):
            return found_lines
        
        target_set = set(target_lines)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                line_number = 0
                
                for line in f:
                    line_number += 1
                    if line_number in target_set:
                        found_lines[line_number] = line.strip()
                        target_set.remove(line_number)
                        if not target_set:  # Found all target lines
                            break
                            
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        
        return found_lines
    
    def generate_fix_script(self, comparison_data: Dict) -> str:
        """Generate a script to fix article numbering issues"""
        script_lines = [
            "#!/usr/bin/env python3",
            '"""',
            "Article Numbering Fix Script",
            "Generated automatically to fix article sequence issues",
            '"""',
            "",
            "import re",
            "import os",
            "",
            "def fix_article_numbering(file_path: str) -> bool:",
            '    """Fix article numbering to be sequential"""',
            "    if not os.path.exists(file_path):",
            "        print(f'File not found: {file_path}')",
            "        return False",
            "",
            "    try:",
            "        with open(file_path, 'r', encoding='utf-8') as f:",
            "            lines = f.readlines()",
            "",
            "        fixed_lines = []",
            "        main_article_counter = 1",
            "",
            "        for line in lines:",
            "            # Check if this is a main article line (### level)",
            "            match = re.search(r'^(###\\s*ARTÍCULO\\s+)\\d+(\\.-.*)', line.strip(), re.IGNORECASE)",
            "            if match:",
            "                prefix = match.group(1)",
            "                suffix = match.group(2)",
            "                # Replace with sequential number",
            "                new_line = f'{prefix}{main_article_counter}{suffix}\\n'",
            "                fixed_lines.append(new_line)",
            "                main_article_counter += 1",
            "            else:",
            "                fixed_lines.append(line)",
            "",
            "        # Write back to file",
            "        with open(file_path, 'w', encoding='utf-8') as f:",
            "            f.writelines(fixed_lines)",
            "",
            "        print(f'Fixed {main_article_counter - 1} main articles in {file_path}')",
            "        return True",
            "",
            "    except Exception as e:",
            "        print(f'Error fixing file {file_path}: {e}')",
            "        return False",
            "",
            "if __name__ == '__main__':",
            "    import sys",
            "    if len(sys.argv) != 2:",
            "        print('Usage: python fix_articles.py <file_path>')",
            "        sys.exit(1)",
            "",
            "    file_path = sys.argv[1]",
            "    success = fix_article_numbering(file_path)",
            "    if success:",
            "        print('Article numbering fixed successfully!')",
            "    else:",
            "        print('Failed to fix article numbering!')",
            "        sys.exit(1)"
        ]
        
        return "\n".join(script_lines)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze article sequence issues between processing steps')
    parser.add_argument('step5_file', help='Path to Step 5 file')
    parser.add_argument('step6_file', help='Path to Step 6 file')
    parser.add_argument('--generate-fix', action='store_true', help='Generate fix script')
    
    args = parser.parse_args()
    
    analyzer = ArticleSequenceAnalyzer()
    comparison_data = analyzer.compare_steps(args.step5_file, args.step6_file)
    
    if args.generate_fix:
        fix_script = analyzer.generate_fix_script(comparison_data)
        fix_script_path = "fix_article_numbering.py"
        
        with open(fix_script_path, 'w', encoding='utf-8') as f:
            f.write(fix_script)
        
        print(f"\n✅ Fix script generated: {fix_script_path}")
        print("Usage: python fix_article_numbering.py <file_path>")

if __name__ == "__main__":
    main()
