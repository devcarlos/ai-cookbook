import re
import sys

def fix_malformed_article_headers(lines):
    fixed_lines = []
    i = 0
    fixes_applied = 0
    while i < len(lines):
        line = lines[i]
        header_match = re.match(r'^(#+\s*ARTÍCULO\s+\d+\.-)\s*$', line.strip())
        if header_match:
            # Look ahead for the title
            j = i + 1
            title_found = False
            while j < len(lines) and j < i + 5: # Look ahead up to 4 lines
                next_line = lines[j].strip()
                if not next_line or next_line == '-':
                    j += 1
                    continue
                
                title_match = re.match(r'^-?\s*(\(.*\))\.$', next_line)
                if not title_match:
                    title_match = re.match(r'^-?\s*(\(.*\))', next_line)

                if title_match:
                    title = title_match.group(1)
                    # Combine header and title
                    new_line = f"{header_match.group(1).strip()} {title}\n"
                    fixed_lines.append(new_line)
                    fixes_applied += 1
                    i = j + 1
                    title_found = True
                    break
                else:
                    break # Not the pattern we are looking for
            
            if not title_found:
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
            
    print(f"Malformed article headers fixed: {fixes_applied}")
    return fixed_lines

def fix_double_accents(lines):
    fixed_lines = []
    fixes_applied = 0
    for line in lines:
        original_line = line
        line = line.replace('ÁÁ', 'Á')
        if original_line != line:
            fixes_applied += 1
        fixed_lines.append(line)
    print(f"Double accent fixes: {fixes_applied}")
    return fixed_lines


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    lines = fix_malformed_article_headers(lines)
    lines = fix_double_accents(lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
