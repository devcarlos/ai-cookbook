#!/usr/bin/env python3
"""
Article Numbering Fix Script
Generated automatically to fix article sequence issues
"""

import re
import os

def fix_article_numbering(file_path: str) -> bool:
    """Fix article numbering to be sequential"""
    if not os.path.exists(file_path):
        print(f'File not found: {file_path}')
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixed_lines = []
        main_article_counter = 1

        for line in lines:
            # Check if this is a main article line (### level)
            match = re.search(r'^(###\s*ARTÍCULO\s+)\d+(\.-.*)', line.strip(), re.IGNORECASE)
            if match:
                prefix = match.group(1)
                suffix = match.group(2)
                # Replace with sequential number
                new_line = f'{prefix}{main_article_counter}{suffix}\n'
                fixed_lines.append(new_line)
                main_article_counter += 1
            else:
                fixed_lines.append(line)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)

        print(f'Fixed {main_article_counter - 1} main articles in {file_path}')
        return True

    except Exception as e:
        print(f'Error fixing file {file_path}: {e}')
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('Usage: python fix_articles.py <file_path>')
        sys.exit(1)

    file_path = sys.argv[1]
    success = fix_article_numbering(file_path)
    if success:
        print('Article numbering fixed successfully!')
    else:
        print('Failed to fix article numbering!')
        sys.exit(1)