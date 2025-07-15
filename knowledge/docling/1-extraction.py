from docling.document_converter import DocumentConverter
from utils.sitemap import get_sitemap_urls
import os
import re
from urllib.parse import urlparse, unquote
import json

def generate_filename_from_url(url):
    """
    Generate a clean filename from a PDF URL by removing special characters
    and URL encoding while preserving readability.
    """
    # Parse the URL to get the path
    parsed_url = urlparse(url)
    
    # Get the filename from the path
    path = parsed_url.path
    filename = os.path.basename(path)
    
    # Remove the .pdf extension if present
    if filename.lower().endswith('.pdf'):
        filename = filename[:-4]
    
    # URL decode to handle encoded characters like %20, %C2%B0, etc.
    filename = unquote(filename)
    
    # Replace problematic characters with safe alternatives
    # Remove or replace special characters that might cause issues in filenames
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)  # Replace invalid filename chars
    filename = re.sub(r'[°]', 'deg', filename)  # Replace degree symbol
    filename = re.sub(r'[ñÑ]', 'n', filename)  # Replace ñ with n
    filename = re.sub(r'[áàäâ]', 'a', filename)  # Replace accented a
    filename = re.sub(r'[éèëê]', 'e', filename)  # Replace accented e
    filename = re.sub(r'[íìïî]', 'i', filename)  # Replace accented i
    filename = re.sub(r'[óòöô]', 'o', filename)  # Replace accented o
    filename = re.sub(r'[úùüû]', 'u', filename)  # Replace accented u
    
    # Remove multiple consecutive underscores and spaces
    filename = re.sub(r'[_\s]+', '_', filename)
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    # Ensure filename is not empty
    if not filename:
        filename = "document"
    
    return filename

def save_outputs_to_files(markdown_output, json_output, base_filename):
    """
    Save markdown and JSON outputs to files with the given base filename.
    """
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save markdown file
    md_filename = os.path.join(output_dir, f"{base_filename}.md")
    with open(md_filename, 'w', encoding='utf-8') as f:
        f.write(markdown_output)
    print(f"Markdown saved to: {md_filename}")
    
    # Save JSON file
    json_filename = os.path.join(output_dir, f"{base_filename}.json")
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, ensure_ascii=False)
    print(f"JSON saved to: {json_filename}")
    
    return md_filename, json_filename

converter = DocumentConverter()

# --------------------------------------------------------------
# Basic PDF extraction
# --------------------------------------------------------------

# result = converter.convert("https://arxiv.org/pdf/2408.09869")
url = "https://sac.impuestos.gob.bo/formularios/pdf/2.-LEY%20N%C2%B0%202492-05-24.pdf"

filePDF = "LEYES_2.-LEY_N_2492-05-24.pdf"
# Default PDF to ingest
pdf_to_extract = "data/LEYES_2.-LEY_N_2492-05-24.pdf"

result = converter.convert(url)

document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()

# Generate filename from URL and save outputs
base_filename = generate_filename_from_url(url)
print(f"Generated filename: {base_filename}")

# Save both outputs to files
md_file, json_file = save_outputs_to_files(markdown_output, json_output, base_filename)

print(f"\nFiles saved successfully:")
print(f"- Markdown: {md_file}")
print(f"- JSON: {json_file}")

# print("\n" + "="*50)
# print("MARKDOWN OUTPUT:")
# print("="*50)
# print(markdown_output)

# # --------------------------------------------------------------
# # Basic HTML extraction
# # --------------------------------------------------------------

# result = converter.convert("https://ds4sd.github.io/docling/")

# document = result.document
# markdown_output = document.export_to_markdown()
# print(markdown_output)

# # --------------------------------------------------------------
# # Scrape multiple pages using the sitemap
# # --------------------------------------------------------------

# sitemap_urls = get_sitemap_urls("https://ds4sd.github.io/docling/")
# conv_results_iter = converter.convert_all(sitemap_urls)

# docs = []
# for result in conv_results_iter:
#     if result.document:
#         document = result.document
#         docs.append(document)
