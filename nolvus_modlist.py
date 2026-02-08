import os
import glob
import logging
from datetime import datetime
from html import escape
import re
import configparser

# Input parameters
drive = 'D'
game = 'SkyrimSE'
version = '6.0.20'
modlist = 'Nolvus Awakening'
profile = 'Nolvus Awakening'
output_dir = f'{drive}:/Modlists'

# Set up logging
current_date = datetime.now().strftime('%y%m%d')
log_file = f'{drive}:/Modlists/modlist_to_html_nolvus_{current_date}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Paths F:\Nolvus\Instances\Nolvus Awakening\MODS\profiles
# modlist_file = f'{drive}:/Wabbajack/{game}/{modlist}/profiles/{profile}/modlist.txt'
modlist_file = f'{drive}:/Nolvus/Instances/{modlist}/MODS/profiles/{profile}/modlist.txt'

# icon_dir = r'icons'  # Relative path for HTML

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Read modlist.txt
try:
    with open(modlist_file, 'r', encoding='utf-8') as f:
        modlist_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    modlist_lines.reverse()  # Reverse order
    logger.info(f"Read {len(modlist_lines)} lines from {modlist_file}")
except Exception as e:
    logger.error(f"Error reading {modlist_file}: {e}")
    exit(1)

# Process meta.ini files
mod_data = {}
for line in modlist_lines:
    if line.endswith('_separator'):
        continue  # Skip separators
    prefix = line[0] if line[0] in ['-', '+', '*'] else ''
    mod_name = line[1:].strip() if prefix else line.strip()
#     meta_path = f'{drive}:/Wabbajack/{game}/{modlist}/mods/{mod_name}/meta.ini'
    meta_path = f'{drive}:/Nolvus/Instances/{modlist}/MODS/mods/{mod_name}/meta.ini'
    
    if os.path.exists(meta_path):
        try:
            config = configparser.ConfigParser()
            config.read(meta_path)
            mod_id = config.get('General', 'modid', fallback='')
            file_id = config.get('installedFiles', '1\\fileid', fallback='')
            if mod_id and file_id:
                mod_data[mod_name] = {'mod_id': mod_id, 'file_id': file_id}
                logger.info(f"Indexed mod: {mod_name}, ModID={mod_id}, FileID={file_id}")
            else:
                logger.warning(f"Missing modid or fileid in {meta_path}")
        except Exception as e:
            logger.error(f"Error parsing {meta_path}: {e}")
    else:
        logger.warning(f"meta.ini not found for mod: {mod_name} at {meta_path}")

# Generate HTML content
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mods for {modlist} ({profile}) {version}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .list-group {{ max-height: 750px; overflow-y: auto; border: 1px solid #ccc; padding: 10px; margin-top: 10px; }}
        .list-group-item {{ word-break: break-all; }}
        img.icon {{ width: 20px; height: 20px; object-fit: contain; vertical-align: middle; margin-right: 5px; }}
        a {{ text-decoration: none; }}
    </style>
</head>
<body>
    <h1>Mods for {modlist} ({profile}) {version}</h1>
    <ul id="archiveList" class="list-group">
"""
for line in modlist_lines:
    if line.endswith('_separator'):
        separator_name = line[1:-len('_separator')].strip()
        html_content += f'        <li class="list-group-item list-group-item-secondary">&mdash; {escape(separator_name)}</li>\n'
        logger.info(f"Processed separator: {separator_name}")
    else:
        prefix = line[0] if line[0] in ['-', '+', '*'] else ''
        mod_name = line[1:].strip() if prefix else line.strip()
        if mod_name in mod_data:
            mod_id = mod_data[mod_name]['mod_id']
            file_id = mod_data[mod_name]['file_id']
            if mod_id and mod_id != "0":
                game_nexus = 'skyrimspecialedition' if game == 'SkyrimSE' else 'fallout4'
                html_content += f'        <li class="list-group-item">{prefix} <a href="https://www.nexusmods.com/{game_nexus}/mods/{mod_id}">{escape(mod_name)}</a> {file_id}</li>\n'
                logger.info(f"Linked mod: {mod_name}, ModID={mod_id}, FileID={file_id}")
            else:
                html_content += f'        <li class="list-group-item"><i>{prefix} {escape(mod_name)}</i></li>\n'
                logger.info(f"Unmatched mod: {mod_name}")
        else:
            html_content += f'        <li class="list-group-item"><i>{prefix} {escape(mod_name)}</i></li>\n'
            logger.info(f"Unmatched mod: {mod_name}")

html_content += """    </ul>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Save HTML
output_html = os.path.join(output_dir, f'mods_{modlist} ({profile}).html')
try:
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"Saved HTML to {output_html}")
except Exception as e:
    logger.error(f"Error writing {output_html}: {e}")
    exit(1)

# Log completion

logger.info(f"Generated HTML for {modlist} with {len(modlist_lines)} entries")
