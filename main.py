import os
import json
import openai
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel

from utils import split_latex_by_section

# === CONFIGURATION ===
API_KEY = os.environ["OPENAI_API_KEY"]
MODEL = "gpt-4.1"
INSTRUCTIONS_PATH = "instructions.txt"
INPUT_LATEX_PATH = "HIG-21-005.tex"
SUPPORTING_DOCS = "Guidelines.md"
OUTPUT_DIR = "LLM_convention_check"
SPLITTING_METHOD = "section"            # chapter: for section by section, paragraph: for paragraph by paragraph

openai.api_key = API_KEY
os.makedirs(OUTPUT_DIR, exist_ok=True)
client = OpenAI()

with open(INSTRUCTIONS_PATH, 'r') as f:
    instructions = f.read()

with open(SUPPORTING_DOCS, 'r') as f:
    supporting_docs = f.read()

# === LOAD AND SPLIT TEX FILE  ===
with open(INPUT_LATEX_PATH, 'r') as f:
    tex = f.read()

preamble, sections = split_latex_by_section(tex)

# === PREPARE PROMPT AND OUTPUT HANDLING  ===
developer_prompt = instructions + supporting_docs

class convention_check_output(BaseModel):
    revised_text: str
    table_of_changes: str


# === ITERATIVELY UPDATE LATEX TEXT ===
final_sections = []
all_changes = []

for idx, (title, section_text) in enumerate(sections):
    print(rf"Processing section {idx + 1}/{len(sections)}: {title}")

    response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {
            "role": "system", 
            "content": developer_prompt
        },
        {
            "role": "user",
            "content": section_text,
        },
    ],
    text_format=convention_check_output,
    )
    
    llm_output = response['choices'][0]['message']['content']

    suggested_revisions_json = json.loads(llm_output)

    revised_text = suggested_revisions_json["revised_text"]
    table_of_changes = suggested_revisions_json["table_of_changes"]

    final_sections.append(revised_text) # text=TBD
    all_changes.append(table_of_changes)

modified_paper = [preamble] + final_sections


# === SAVE PAPER AND EDITS ===
with open(Path(OUTPUT_DIR) / f"modified_paper.tex", 'w') as f:
    f.write("".join(modified_paper))

with open(Path(OUTPUT_DIR) / f"List_of_changes.txt", 'w') as f:
    f.write("".join(all_changes))
