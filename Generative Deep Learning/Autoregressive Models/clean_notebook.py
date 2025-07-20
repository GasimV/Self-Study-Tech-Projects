import nbformat

path = "MedGemma.ipynb"
notebook = nbformat.read(path, as_version=4)

if 'widgets' in notebook.metadata:
    del notebook.metadata['widgets']

cleaned_path = "MedGemma.ipynb"
with open(cleaned_path, "w", encoding="utf-8") as f:
    nbformat.write(notebook, f)

print(f"Cleaned notebook saved to: {cleaned_path}")