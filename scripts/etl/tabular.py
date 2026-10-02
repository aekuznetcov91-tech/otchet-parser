"""Tabular stage of the dashboard ETL."""
from .normalization import clean_key
from html.parser import HTMLParser
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

class HtmlTableParser(HTMLParser):
    """Fast streaming parser for HTML-based XLS tables."""
    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.current_cell = []
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = []
        elif tag == 'tr':
            self.current_row = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th'):
            self.in_cell = False
            self.current_row.append("".join(self.current_cell).strip())
        elif tag == 'tr':
            if any(self.current_row):
                self.rows.append(self.current_row)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell.append(data)


def extract_rows_from_matrix(matrix):
    """Locate table header row and convert matrix to pre-cleaned dictionary rows."""
    if not matrix:
        return []
    header_idx = -1
    for i, row in enumerate(matrix[:25]):
        non_empty = [c for c in row if c is not None and str(c).strip()]
        if len(non_empty) < 3:
            continue
        row_str = clean_key("".join(str(c) for c in row))
        if 'ПРИМЕНЕННЫЕФИЛЬТРЫ' in row_str:
            continue
        if (
            'ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ' in row_str or
            'EVENTNAME' in row_str or
            ('БИТРИКС' in row_str and 'ПОЧТА' in row_str) or
            ('СТАДИЯСДЕЛКИ' in row_str and 'ТОВАР' in row_str) or
            ('БИТРИКС' in row_str and 'КАМ' in row_str) or
            ('ДАТА' in row_str and ('ЦЕНААВТО' in row_str or 'URL' in row_str or 'ОТВЕТСТВЕННЫЙ' in row_str or 'СУММА' in row_str)) or
            ('CLIENTID' in row_str and ('ПАРТНЕР' in row_str or 'BI' in row_str or 'LINK' in row_str or 'SOURCE' in row_str or 'EVENTNAME' in row_str or 'URL' in row_str)) or
            ('SALEMONTH' in row_str and 'PREPAYMONTH' in row_str) or
            ('ОТВЕТСТВЕННЫЙ' in row_str and 'ПАРТНЕР' in row_str) or
            ('УНИКАЛЬНЫЕКЛИЕНТЫ' in row_str)
        ):
            header_idx = i
            break

    if header_idx == -1:
        for i, row in enumerate(matrix[:25]):
            non_empty = [c for c in row if c is not None and str(c).strip()]
            row_str = clean_key("".join(str(c) for c in row))
            if len(non_empty) >= 3 and 'ПРИМЕНЕННЫЕФИЛЬТРЫ' not in row_str:
                header_idx = i
                break
        if header_idx == -1:
            header_idx = 0

    headers = [str(c).strip() for c in matrix[header_idx]]
    clean_headers = [clean_key(h) for h in headers]
    result = []

    for row in matrix[header_idx + 1:]:
        row_dict = {}
        for h_i, h_name in enumerate(headers):
            if h_name:
                val = row[h_i] if h_i < len(row) else ""
                val_str = val if val is not None else ""
                row_dict[h_name] = val_str
                c_h = clean_headers[h_i]
                if c_h:
                    row_dict[c_h] = val_str
        if any(v != "" for v in row_dict.values()):
            result.append(row_dict)
    return result


def safe_open_rb(filepath):
    """Safely open binary file for reading even if locked exclusively by MS Excel on Windows."""
    try:
        return open(filepath, 'rb')
    except PermissionError:
        if sys.platform == 'win32':
            try:
                import ctypes, msvcrt
                GENERIC_READ = 0x80000000
                FILE_SHARE_READ = 1
                FILE_SHARE_WRITE = 2
                FILE_SHARE_DELETE = 4
                OPEN_EXISTING = 3
                FILE_ATTRIBUTE_NORMAL = 0x80
                handle = ctypes.windll.kernel32.CreateFileW(
                    os.path.abspath(filepath),
                    GENERIC_READ,
                    FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                    None,
                    OPEN_EXISTING,
                    FILE_ATTRIBUTE_NORMAL,
                    None
                )
                if handle not in (0, -1):
                    fd = msvcrt.open_osfhandle(handle, os.O_RDONLY)
                    return open(fd, 'rb')
            except Exception:
                pass
        raise


def read_xlsx_xml(filepath):
    """High-performance direct streaming parser for zipped XLSX XML files."""
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    datasets = []
    try:
        fp = safe_open_rb(filepath)
    except Exception:
        return []

    try:
        with zipfile.ZipFile(fp, 'r') as z:
            # 1. Read shared strings
            ss = []
            if 'xl/sharedStrings.xml' in z.namelist():
                tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
                for si in tree.findall(f'{ns}si'):
                    text_parts = [t.text for t in si.iter(f'{ns}t') if t.text]
                    ss.append("".join(text_parts))

            # 2. Find sheets
            sheet_files = [n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
            for sname in sheet_files:
                sheet_tree = ET.fromstring(z.read(sname))
                matrix = []
                for r_node in sheet_tree.findall(f'.//{ns}row'):
                    row_dict = {}
                    max_col = 0
                    for c_node in r_node.findall(f'{ns}c'):
                        r_ref = c_node.attrib.get('r', '')
                        col_match = re.match(r'([A-Z]+)', r_ref)
                        if col_match:
                            col_str = col_match.group(1)
                            col_idx = 0
                            for ch in col_str:
                                col_idx = col_idx * 26 + (ord(ch) - ord('A') + 1)
                            col_idx -= 1
                        else:
                            col_idx = max_col

                        max_col = max(max_col, col_idx + 1)

                        t_attr = c_node.attrib.get('t')
                        v_node = c_node.find(f'{ns}v')
                        val = v_node.text if v_node is not None else ""

                        if t_attr == 's' and val.isdigit():
                            idx = int(val)
                            val = ss[idx] if idx < len(ss) else val
                        elif t_attr == 'inlineStr':
                            is_node = c_node.find(f'{ns}is')
                            if is_node is not None:
                                t_parts = [t.text for t in is_node.iter(f'{ns}t') if t.text]
                                val = "".join(t_parts)

                        row_dict[col_idx] = val

                    if row_dict:
                        num_cols = max(row_dict.keys()) + 1
                        row_list = [row_dict.get(c, "") for c in range(num_cols)]
                        matrix.append(row_list)

                parsed = extract_rows_from_matrix(matrix)
                if parsed:
                    short_name = sname.split('/')[-1]
                    datasets.append((short_name, parsed))

        return datasets
    except Exception:
        return []
    finally:
        try:
            fp.close()
        except Exception:
            pass


def read_tabular_file(filepath):
    """Read CSV, HTML/XLS, or XLSX file format dynamically with error tolerance."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in ('.xlsx', '.xlsm'):
        datasets = read_xlsx_xml(filepath)
        if datasets:
            return datasets
        try:
            import openpyxl
            wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
            for sname in wb.sheetnames:
                ws = wb[sname]
                matrix = [list(r) for r in ws.iter_rows(values_only=True) if any(cell is not None for cell in r)]
                parsed = extract_rows_from_matrix(matrix)
                if parsed:
                    datasets.append((sname, parsed))
            wb.close()
            return datasets
        except Exception:
            return []

    # Handle HTML table or CSV
    datasets = []
    with safe_open_rb(filepath) as f:
        raw_bytes = f.read()

    encoding = 'windows-1251'
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        encoding = 'utf-8-sig'
    elif b'charset=utf-8' in raw_bytes[:500].lower() or b'charset="utf-8"' in raw_bytes[:500].lower():
        encoding = 'utf-8'

    try:
        text = raw_bytes.decode(encoding)
    except Exception:
        text = raw_bytes.decode('windows-1251', errors='ignore')

    if '<table' in text.lower() or '<tr' in text.lower():
        p = HtmlTableParser()
        p.feed(text)
        parsed_rows = extract_rows_from_matrix(p.rows)
        if parsed_rows:
            datasets.append(('main', parsed_rows))
    else:
        sample = text[:2048]
        delimiter = ';' if sample.count(';') > sample.count(',') else ','
        reader = csv.reader(text.splitlines(), delimiter=delimiter)
        matrix = [r for r in reader if any(r)]
        parsed_rows = extract_rows_from_matrix(matrix)
        if parsed_rows:
            datasets.append(('main', parsed_rows))

    return datasets


def identify_data_type(rows):
    """Classify dataset schema into 'deals', 'leads', 'directory', or 'unknown'."""
    if not rows:
        return "unknown"
    headers_str = clean_key("".join(str(k) for k in rows[0].keys()))

    if ('СТАДИЯСДЕЛКИ' in headers_str and ('ПРЕДПОЛАГАЕМАЯДАТАЗАКРЫТИЯ' in headers_str or 'ТОВАР' in headers_str or 'КОМИССИЯСДЕЛКИРУБ' in headers_str)) or ('SALEMONTH' in headers_str and 'PREPAYMONTH' in headers_str):
        return "deals"
    if 'EVENTNAME' in headers_str or ('ДАТА' in headers_str and 'ЦЕНААВТО' in headers_str) or ('CLIENTID' in headers_str and ('ПАРТНЕР' in headers_str or 'BI' in headers_str or 'LINK' in headers_str or 'SOURCE' in headers_str)):
        return "leads"
    if 'БИТРИКС' in headers_str or ('КАМ' in headers_str and 'BI' in headers_str):
        return "directory"

    return "unknown"

