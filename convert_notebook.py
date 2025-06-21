import nbformat
from nbconvert import PythonExporter

# Read the notebook with UTF-8 encoding
with open('KT_Project_3_serv_GF_base.ipynb', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

# Convert to Python
exporter = PythonExporter()
python_code, _ = exporter.from_notebook_node(nb)

# Write to file with UTF-8 encoding
with open('KT_Project_3_serv_GF_base.py', 'w', encoding='utf-8') as f:
    f.write(python_code)

print("Conversion complete! Check KT_Project_3_serv_GF_base.py") 