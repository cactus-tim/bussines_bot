import importlib
import inspect
import os
import shutil
import subprocess
from time import time

# Глобальные настройки по умолчанию
PROJECT_NAME = "HSE Buisness Club Telegram-bot"
DEFAULT_AUTHOR = "HSE IT Team"
DEFAULT_RELEASE = "v3.0.0"
DEFAULT_YEAR = "2025"
CREATE_PDF = True

# pip install sphinx sphinx_togglebutton sphinx_rtd_theme

DOCS_SOURCE = "docs/source"
# Исключаем папки с django-приложением и служебными файлами
EXCLUDE_DIRS = {".venv", "venv", ".git", "__pycache__", ".idea", ".vscode", ".github",
                "isp-files", "files", "old_docs", ".env"}
EXCLUDE_FILES = {"conf.py", "generate_docs.py", 'test.py'}


def clean_old_docs():
    """
    Удаляет старые .rst файлы (кроме conf.py) и папку _build.
    """
    for dirpath, _, filenames in os.walk(DOCS_SOURCE):
        for filename in filenames:
            if filename.endswith(".rst") and filename != "conf.py":
                try:
                    os.remove(os.path.join(dirpath, filename))
                except Exception:
                    pass
    build_dir = os.path.join("docs", "_build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)


def clean_latex_intermediate_files():
    """
    В docs/_build/latex удаляются все файлы и папки, кроме PDF.
    """
    latex_dir = os.path.join("docs", "_build", "latex")
    if not os.path.exists(latex_dir):
        return
    for entry in os.scandir(latex_dir):
        full_path = entry.path
        try:
            if entry.is_file():
                if not full_path.lower().endswith(".pdf"):
                    os.remove(full_path)
            elif entry.is_dir():
                shutil.rmtree(full_path, ignore_errors=True)
        except Exception:
            continue


def move_build_output():
    """
    Перемещает сгенерированные папки из docs/_build в docs.
    Если есть папка latex – переименовывает её в pdf.
    """
    build_dir = os.path.join("docs", "_build")
    html_src = os.path.join(build_dir, "html")
    latex_src = os.path.join(build_dir, "latex")
    dest_html = os.path.join("docs", "html")
    dest_pdf = os.path.join("docs", "pdf")
    if os.path.exists(html_src):
        if os.path.exists(dest_html):
            shutil.rmtree(dest_html, ignore_errors=True)
        shutil.move(html_src, dest_html)
    if os.path.exists(latex_src):
        if os.path.exists(dest_pdf):
            shutil.rmtree(dest_pdf, ignore_errors=True)
        shutil.move(latex_src, dest_pdf)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)


def build_package_tree(root="."):
    """
    Рекурсивно проходит по директории проекта и строит дерево пакетов/модулей.
    """
    rel_path = os.path.relpath(root, start=".")
    # Пропускаем папку docs, чтобы не рекурсировать в неё
    if "docs" in rel_path.split(os.sep):
        return {}
    root_name = os.path.basename(root.rstrip(os.sep))
    if root_name in EXCLUDE_DIRS:
        return {}
    tree = {}
    try:
        with os.scandir(root) as it:
            entries = list(it)
    except Exception:
        return {}
    is_package = any(e.name == "__init__.py" for e in entries if e.is_file())
    for entry in entries:
        full_path = os.path.join(root, entry.name)
        if entry.is_dir():
            subtree = build_package_tree(full_path)
            if subtree:
                tree[entry.name] = subtree
        else:
            if entry.name.endswith(".py") and entry.name not in EXCLUDE_FILES:
                mod_name = os.path.splitext(entry.name)[0]
                tree[mod_name] = None
    if is_package:
        tree["__init__"] = True
    return tree


def get_last_segment(dotted_path: str, default: str = "") -> str:
    """
    Возвращает последний сегмент строки, разделённой точками.
    """
    if not dotted_path:
        return default
    parts = dotted_path.split(".")
    return parts[-1] if parts else default


def extract_constants(file_path):
    """
    Извлекает константы из файла модуля.
    Константой считается переменная с именем, состоящим из заглавных букв (и подчёркиваний).
    """
    import ast
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return []
    try:
        tree = ast.parse(source)
    except Exception:
        return []
    lines = source.splitlines()
    constants = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    if name.isupper() or (all(c.isupper() or c == '_' for c in name) and name.strip('_')):
                        type_str = ""
                        if isinstance(node, ast.AnnAssign) and node.annotation is not None:
                            if hasattr(ast, "unparse"):
                                try:
                                    type_str = ast.unparse(node.annotation)
                                except Exception:
                                    type_str = ""
                        line = lines[node.lineno - 1]
                        comment = line.split('#', 1)[1].strip() if '#' in line else ""
                        constants.append({
                            "name": name,
                            "type": type_str,
                            "comment": comment
                        })
    return constants


def extract_class_attributes(file_path, class_name):
    """
    Извлекает атрибуты класса с комментариями из исходного файла.
    Если комментарий указан в той же строке – он включается в документацию.
    """
    import ast
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception:
        return []
    try:
        tree = ast.parse(source)
    except Exception:
        return []
    lines = source.splitlines()
    attributes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.Assign, ast.AnnAssign)):
                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                    for target in targets:
                        if isinstance(target, ast.Name):
                            name = target.id
                            lineno = item.lineno
                            line = lines[lineno - 1] if lineno - 1 < len(lines) else ""
                            comment = ""
                            if '#' in line:
                                comment = line.split('#', 1)[1].strip()
                            if comment:
                                type_str = ""
                                if isinstance(item, ast.AnnAssign) and item.annotation is not None:
                                    if hasattr(ast, "unparse"):
                                        try:
                                            type_str = ast.unparse(item.annotation)
                                        except Exception:
                                            type_str = ""
                                attributes.append({
                                    "name": name,
                                    "type": type_str,
                                    "comment": comment
                                })
            break
    return attributes


def extract_module_description(file_path):
    """
    Извлекает описание модуля из файла (обычно __init__.py).
    Если в начале присутствует docstring – используется он, иначе собираются подряд идущие комментарии.
    При этом символы перевода строки заменяются на HTML-тег <br> для корректного отображения.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception:
        return ""
    lines = [line.rstrip() for line in lines if line.strip() and not line.startswith("#!")]
    description_lines = []
    if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
        quote = lines[0][:3]
        if lines[0].endswith(quote) and len(lines[0]) > 3:
            return lines[0][3:-3].strip().replace("\\n", " <br>\\n")
        else:
            for line in lines[1:]:
                if line.endswith(quote):
                    break
                description_lines.append(line)
            return "\n".join(description_lines).strip().replace("\\n", " <br>\n")
    for line in lines:
        if line.startswith("#"):
            description_lines.append(line.lstrip("# ").rstrip())
        else:
            break
    return "\n".join(description_lines).strip().replace("\\n", " <br>\\n")


def remove_orphan_directive(dir_path):
    """
    Рекурсивно удаляет директиву '.. orphan:' из всех .rst файлов в заданной папке.
    """
    for root, _, files in os.walk(dir_path):
        for file in files:
            if file.endswith(".rst"):
                full_path = os.path.join(root, file)
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    new_content = content.replace(".. orphan:", "")
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                except Exception:
                    continue


def write_package_docs(tree, parent_dir="", parent_mod_path=""):
    """
    Рекурсивно генерирует .rst файлы для пакетов и модулей.
    (Оставляем эту функцию для модулей, входящих в основной проект.)
    """
    if not tree:
        return

    current_dir = DOCS_SOURCE if not parent_dir else parent_dir
    if parent_mod_path:
        current_dir = os.path.join(DOCS_SOURCE, parent_mod_path.replace(".", "/"))
    os.makedirs(current_dir, exist_ok=True)

    subpackages = []
    modules = []
    for name, subtree in sorted(tree.items()):
        if name == "__init__":
            continue
        if subtree is None:
            modules.append(name)
        else:
            subpackages.append(name)

    if not subpackages and not modules:
        return

    # Генерация index.rst для пакета
    index_path = os.path.join(current_dir, "index.rst")
    safe_title = get_last_segment(parent_mod_path, default=f"{PROJECT_NAME} Documentation")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(f"{safe_title}\n{'=' * len(safe_title)}\n\n")
        if parent_mod_path:
            try:
                pkg = importlib.import_module(parent_mod_path)
                pkg_doc = inspect.getdoc(pkg)
                if not pkg_doc and getattr(pkg, '__file__', None):
                    pkg_doc = extract_module_description(pkg.__file__)
            except Exception:
                pkg_doc = ""
            if pkg_doc:
                f.write(pkg_doc + "\n\n")
        f.write(".. contents::\n   :local:\n   :depth: 2\n\n")
        f.write(".. toctree::\n   :maxdepth: 1\n   :titlesonly:\n   :glob:\n\n")
        for subpkg in subpackages:
            f.write(f"   {subpkg}/index\n")
        for mod in modules:
            f.write(f"   {mod}\n")
        f.write("\n")

    for mod in modules:
        mod_full_path = f"{parent_mod_path}.{mod}" if parent_mod_path else mod
        rst_path = os.path.join(current_dir, mod + ".rst")
        safe_module_name = get_last_segment(mod_full_path, default=mod_full_path)
        mod_file = None
        try:
            module_obj = importlib.import_module(mod_full_path)
            doc = inspect.getdoc(module_obj)
            mod_file = getattr(module_obj, '__file__', None)
            if not doc and mod_file and mod_file.endswith(".py"):
                doc = extract_module_description(mod_file)
        except Exception:
            doc = ""
            module_obj = None

        with open(rst_path, "w", encoding="utf-8") as f_mod:
            f_mod.write(f"{safe_module_name}\n{'=' * len(safe_module_name)}\n\n")
            if module_obj and mod_file and mod_file.endswith(".py"):
                try:
                    classes_in_mod = [
                        obj.__name__
                        for name, obj in inspect.getmembers(module_obj, inspect.isclass)
                        if obj.__module__ == mod_full_path
                    ]
                except Exception:
                    classes_in_mod = []
            else:
                classes_in_mod = []
            exclude_members = ""
            if classes_in_mod:
                exclude_members = "   :exclude-members: " + ",".join(classes_in_mod) + "\n"
            f_mod.write(f".. automodule:: {mod_full_path}\n")
            f_mod.write("   :members:\n")
            f_mod.write("   :undoc-members:\n")
            f_mod.write("   :show-inheritance:\n")
            if exclude_members:
                f_mod.write(exclude_members)
            f_mod.write("\n")
            if mod_file and mod_file.endswith(".py"):
                constants = extract_constants(mod_file)
            else:
                constants = []
            if constants:
                f_mod.write("Constants\n---------\n\n")
                for const in constants:
                    f_mod.write(f".. py:data:: {const['name']}\n")
                    if const['type']:
                        f_mod.write(f"   :type: {const['type']}\n")
                    f_mod.write("\n")
                    if const['comment']:
                        f_mod.write(f"   {const['comment']}\n\n")
                    else:
                        f_mod.write("\n")
            if mod_file and mod_file.endswith(".py"):
                try:
                    classes = [
                        obj for name, obj in inspect.getmembers(module_obj, inspect.isclass)
                        if obj.__module__ == mod_full_path
                    ]
                except Exception:
                    classes = []
                for cls in classes:
                    cls_name = cls.__name__
                    attrs = extract_class_attributes(mod_file, cls_name)
                    exclude_attr_names = ",".join(attr["name"] for attr in attrs if attr["comment"].strip())
                    f_mod.write(f".. autoclass:: {mod_full_path}.{cls_name}\n")
                    if exclude_attr_names:
                        f_mod.write(f"   :exclude-members: {exclude_attr_names}\n")
                    f_mod.write("   :members:\n")
                    f_mod.write("   :undoc-members:\n")
                    f_mod.write("   :show-inheritance:\n\n")
                    for attr in attrs:
                        if attr["comment"].strip():
                            f_mod.write(f"   .. py:attribute:: {attr['name']}\n")
                            if attr["type"].strip():
                                f_mod.write(f"      :type: {attr['type']}\n")
                            f_mod.write("\n")
                            f_mod.write(f"      {attr['comment']}\n\n")
    for subpkg in sorted([name for name in tree.keys() if tree[name] is not None and name != "__init__"]):
        new_mod_path = f"{parent_mod_path}.{subpkg}" if parent_mod_path else subpkg
        write_package_docs(tree[subpkg], parent_dir="", parent_mod_path=new_mod_path)


def build_docs():
    """
    Генерирует HTML документацию с помощью sphinx-build.
    """
    os.makedirs(os.path.join("docs", "_static"), exist_ok=True)
    subprocess.run(["sphinx-build", "-b", "html", "source", "_build/html"],
                   cwd="docs", stdout=subprocess.DEVNULL)


def build_pdf():
    """
    Генерирует PDF документацию.
    Сначала генерирует LaTeX-источники с помощью sphinx-build, затем компилирует PDF с pdflatex.
    """
    subprocess.run(["sphinx-build", "-b", "latex", "source", "_build/latex"],
                   cwd="docs", stdout=subprocess.DEVNULL)
    if shutil.which("pdflatex"):
        subprocess.run(["pdflatex", f"{PROJECT_NAME}.tex"],
                       cwd=os.path.join("docs", "_build", "latex"), stdout=subprocess.DEVNULL)


def init_sphinx():
    """
    Инициализирует конфигурацию Sphinx.
    Выполняется django.setup() для корректной работы autodoc с Django.
    """
    global PROJECT_NAME, CREATE_PDF

    print("Current default settings:")
    print(f"1. Project name: {PROJECT_NAME}")
    print(f"2. Author: {DEFAULT_AUTHOR}")
    print(f"3. Project version: {DEFAULT_RELEASE}")
    print(f"4. Copyright year: {DEFAULT_YEAR}")
    print(f"6. Create PDF: {'Yes' if CREATE_PDF else 'No'}")
    use_defaults = input("Use default settings? (y/n): ").strip().lower() == 'y'

    if not use_defaults:
        PROJECT_NAME = input(f"Project name [{PROJECT_NAME}]: ").strip() or PROJECT_NAME
        author = input(f"Project author [{DEFAULT_AUTHOR}]: ").strip() or DEFAULT_AUTHOR
        release = input(f"Project version [{DEFAULT_RELEASE}]: ").strip() or DEFAULT_RELEASE
        year = input(f"Copyright year [{DEFAULT_YEAR}]: ").strip() or DEFAULT_YEAR
        create_pdf_input = input("Create PDF documentation? (y/n) [y]: ").strip().lower() or 'y'
        CREATE_PDF = (create_pdf_input == 'y')
    else:
        author = DEFAULT_AUTHOR
        release = DEFAULT_RELEASE
        year = DEFAULT_YEAR

    os.makedirs("docs/source", exist_ok=True)
    os.makedirs("docs/_build", exist_ok=True)
    os.makedirs("docs/_static", exist_ok=True)
    os.makedirs("docs/_templates", exist_ok=True)

    conf_content = f"""# Sphinx configuration file
suppress_warnings = ['orphan']
project = '{PROJECT_NAME}'
copyright = '{DEFAULT_YEAR}, {DEFAULT_AUTHOR}'
author = '{DEFAULT_AUTHOR}'
release = '{DEFAULT_RELEASE}'

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_togglebutton'
]
templates_path = ['_templates']
exclude_patterns = ['**/migrations']

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

autodoc_member_order = 'bysource'

latex_engine = 'pdflatex'
latex_elements = {{
    'classoptions': ',russian,openany',
    'preamble': r'''\\usepackage[T2A]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
''',
    'printindex': '',
}}
latex_domain_indices = False
latex_use_index = False

latex_documents = [
    ('index', '{PROJECT_NAME}.tex', '{PROJECT_NAME} Documentation',
     '{DEFAULT_AUTHOR}', 'manual', True),
]
"""
    conf_path = os.path.join("docs", "source", "conf.py")
    with open(conf_path, "w", encoding="utf-8") as f:
        f.write(conf_content)

    index_content = f"""{PROJECT_NAME} Documentation
=====================

Welcome to the documentation for {PROJECT_NAME}.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   django_docs/*
"""
    index_path = os.path.join("docs", "source", "index.rst")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)


def clean_intermediate_files():
    """
    Удаляет все файлы и папки в docs, кроме _build.
    """
    docs_dir = "docs"
    for entry in os.listdir(docs_dir):
        if entry != "_build":
            full_path = os.path.join(docs_dir, entry)
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path, ignore_errors=True)
                else:
                    os.remove(full_path)
            except Exception:
                continue


def main():
    """
    Основная функция генерации документации.
    """
    start_time = time()

    if not os.path.exists("docs") or not os.path.exists(os.path.join("docs", "source", "conf.py")):
        init_sphinx()

    clean_old_docs()

    tree = build_package_tree(root=".")
    top_index_path = os.path.join(DOCS_SOURCE, "index.rst")
    with open(top_index_path, "w", encoding="utf-8") as f:
        title = f"{PROJECT_NAME} Documentation"
        f.write(f"{title}\n{'=' * len(title)}\n\n")
        f.write(".. toctree::\n")
        f.write("   :maxdepth: 1\n")
        f.write("   :titlesonly:\n")
        f.write("   :glob:\n\n")
        for name in sorted(tree.keys()):
            if name == "__init__":
                continue
            if tree[name] is None:
                f.write(f"   {name}\n")
            else:
                f.write(f"   {name}/index\n")

    write_package_docs(tree, parent_dir="", parent_mod_path="")

    build_docs()

    if CREATE_PDF:
        build_pdf()
        clean_latex_intermediate_files()

    clean_intermediate_files()
    move_build_output()

    total_time = time() - start_time
    print(f"Documentation built in {total_time:.1f} seconds.")


if __name__ == "__main__":
    main()
