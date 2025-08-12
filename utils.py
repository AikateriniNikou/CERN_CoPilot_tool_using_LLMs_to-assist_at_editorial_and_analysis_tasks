import os
import re
import json
import openai
from pathlib import Path

def split_latex_by_section(tex: str):
    section_pattern = re.compile(r'\\section\{(.*?)\}', re.DOTALL)
    preamble_end_pattern = re.compile(r'\\cmsNoteHeader\{(.*?)\}', re.DOTALL)

    preamble_end_pattern = list(preamble_end_pattern.finditer(tex))
    section_matches = list(section_pattern.finditer(tex))

    if not section_matches:
        return [("No Section", tex)]

    sections = []

    abstract_and_title_start = preamble_end_pattern[0].start()
    first_section_start = section_matches[0].start()

    preamble = tex[:abstract_and_title_start]
    title_and_abstract = tex[abstract_and_title_start:first_section_start]

    # Save the title and abstract as a section
    sections.append(("Title and abstract", title_and_abstract))

    # Add the remaining sections
    for i, match in enumerate(section_matches):
        section_title = match.group(1)
        start = match.start()
        end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(tex)
        section_text = tex[start:end]
        sections.append((section_title, section_text))

    return preamble, sections
