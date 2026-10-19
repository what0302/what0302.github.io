from pathlib import Path
import shutil

base = Path.home() / 'Desktop' / 'RansomDemo'
target = base / 'critical_EUID'
source = Path(__file__).resolve().parent

files = {
    'project_description.txt': 'CSCE 5550 Ransomware Project\nTraining copy only.\n',
    'folder1/lab_notes.txt': 'Lab notes\nThis is sample data for encryption testing.\n',
    'folder1/grades.csv': 'name,grade\nAlice,95\nBob,88\n',
    'folder2/settings.json': '{"mode": "training", "active": true}\n',
    'folder3/assignment.md': '# Homework\nExplain hybrid encryption.\n',
    'folder3/record.log': '2026-10-19 INFO Test file created\n',
}

if target.exists():
    print('Folder already exists. Nothing changed:', target)
else:
    for name, content in files.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    print('Created sample project files:', target)
print('Replace EUID and sample contents with the required course materials before final submission.')
