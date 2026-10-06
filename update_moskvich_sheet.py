import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from copy import copy

FILE_PATH = 'raw_data/OEM СберАвто финал (15).xlsx'

def update_moskvich():
    wb = openpyxl.load_workbook(FILE_PATH)
    # Find Moskvich sheet
    sheet_name = None
    for name in wb.sheetnames:
        if 'Москвич' in name or name.strip() == 'Москвич':
            sheet_name = name
            break
    if not sheet_name:
        raise ValueError('Moskvich sheet not found!')
    
    ws = wb[sheet_name]
    print(f'Found sheet: {repr(sheet_name)}')

    # 1. Read existing dealer data (from row 2 onwards)
    dealer_rows = []
    for r in range(2, ws.max_row + 1):
        row_data = []
        for c in range(1, ws.max_column + 1):
            cell = ws.cell(r, c)
            row_data.append({
                'value': cell.value,
                'font': copy(cell.font) if cell.font else None,
                'fill': copy(cell.fill) if cell.fill else None,
                'alignment': copy(cell.alignment) if cell.alignment else None,
                'border': copy(cell.border) if cell.border else None,
                'number_format': cell.number_format,
                'hyperlink': copy(cell.hyperlink) if cell.hyperlink else None,
            })
        if any(d['value'] is not None for d in row_data):
            dealer_rows.append(row_data)

    print(f'Extracted {len(dealer_rows)} dealer rows (including header)')

    # Clear worksheet contents
    for row in ws.iter_rows():
        for cell in row:
            cell.value = None
            cell.fill = PatternFill(fill_type=None)
            cell.border = Border()
            cell.hyperlink = None

    # Get sample styles from CHERY&TENET
    ws_sample = wb['CHERY&TENET']
    header_fill = copy(ws_sample['A4'].fill)
    header_font = Font(name='Arial', size=10, bold=False, color='000000')
    title_font = Font(name='Arial', size=10, bold=True, color='000000')
    data_font = Font(name='Arial', size=10, bold=False, color='000000')
    
    thin_border_side = Side(style='thin', color='D9D9D9')
    table_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='center')
    right_align = Alignment(horizontal='right', vertical='center')

    ruble_format = '#,##0\\ _р_._'  # or '#,##0 "₽"' or '#,##0'
    # Let's check number format on CHERY&TENET E5
    sample_price_fmt = ws_sample['E5'].number_format

    # Set Sheet Title rows
    # Row 1: КАТЕГОРИЯ: ОНЛАЙН
    ws['A1'].value = 'КАТЕГОРИЯ: ОНЛАЙН'
    ws['A1'].font = title_font
    ws['A1'].alignment = left_align

    # Row 2: Обновлено: 22.09.2026
    ws['A2'].value = 'Обновлено: 22.09.2026'
    ws['A2'].font = data_font
    ws['A2'].alignment = left_align

    # Row 3: Headers
    headers = [
        'Марка',
        'Модель',
        'Комплектация',
        'Год',
        'РРЦ',
        'Скидка клиенту',
        'Цена для клиента'
    ]

    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=3, column=col_idx)
        c.value = h
        c.font = header_font
        c.fill = copy(header_fill)
        c.alignment = center_align
        c.border = table_border

    # Car data (15 rows)
    cars_data = [
        # Москвич 3 (2025)
        ('Москвич', '3', 'Стандарт Плюс Телематика 1,5Т МКП6', 2025, 1952000, 0, 1952000),
        ('Москвич', '3', 'Стандарт Плюс Телематика 1,5T вариатор', 2025, 2041000, 0, 2041000),
        ('Москвич', '3', 'Комфорт Телематика 1,5T вариатор', 2025, 2175000, 0, 2175000),
        # Москвич 3 (2026)
        ('Москвич', '3', 'Стандарт Телематика 2026 1,5Т МКП6', 2026, 2040000, 0, 2040000),
        ('Москвич', '3', 'Стандарт Телематика 2026 1,5T вариатор', 2026, 2150000, 0, 2150000),
        ('Москвич', '3', 'Стандарт Плюс Телематика 2026 1,5Т МКП6', 2026, 2040000, 0, 2040000),
        ('Москвич', '3', 'Стандарт Плюс Телематика 2026 1,5T вариатор', 2026, 2135000, 0, 2135000),
        ('Москвич', '3', 'Комфорт Телематика 2026 1,5T вариатор', 2026, 2280000, 0, 2280000),
        # Москвич 8 (2025)
        ('Москвич', '8', 'Бизнес, 1,5Т (7DCT)', 2025, 3125000, 0, 3125000),
        ('Москвич', '8', 'Техно, 1,5Т (7DCT)', 2025, 3350000, 0, 3350000),
        ('Москвич', '8', 'Премиум, 1,5Т (7DCT)', 2025, 3515000, 0, 3515000),
        # Москвич 8 (2026)
        ('Москвич', '8', 'Техно Телематика, 1,5Т (7DCT)', 2026, 3535000, 0, 3535000),
        # Москвич М70 (2026)
        ('Москвич', 'М70', 'DRIVE (ДРАЙВ) 1.5T 7DCT', 2026, 3099000, 0, 3099000),
        ('Москвич', 'М70', 'ULTRA (УЛЬТРА) 2.0T 9AT', 2026, 3499000, 0, 3499000),
        # Москвич М90 (2026)
        ('Москвич', 'М90', 'ULTIMATE (УЛЬТИМЕЙТ) 2.0T 9AT 4WD', 2026, 4199000, 0, 4199000),
    ]

    for idx, row in enumerate(cars_data, start=4):
        for col_idx, val in enumerate(row, start=1):
            c = ws.cell(row=idx, column=col_idx)
            c.value = val
            c.font = data_font
            c.border = table_border
            if col_idx in [1, 2, 4]:
                c.alignment = center_align
            elif col_idx == 3:
                c.alignment = left_align
            elif col_idx in [5, 6, 7]:
                c.alignment = right_align
                c.number_format = sample_price_fmt

    # Row 19 is empty spacer
    # Row 20: приоритет с актуальным стоком и ценой
    # Row 21: приоритет
    prio_row1 = 20
    prio_row2 = 21

    ws.cell(row=prio_row1, column=2).value = 'приоритет с актуальным стоком и ценой'
    ws.cell(row=prio_row1, column=2).font = data_font
    if ws_sample['B23'].fill and ws_sample['B23'].fill.fill_type:
        ws.cell(row=prio_row1, column=2).fill = copy(ws_sample['B23'].fill)

    ws.cell(row=prio_row2, column=2).value = 'приоритет'
    ws.cell(row=prio_row2, column=2).font = data_font
    if ws_sample['B24'].fill and ws_sample['B24'].fill.fill_type:
        ws.cell(row=prio_row2, column=2).fill = copy(ws_sample['B24'].fill)

    # Row 22 is empty spacer
    # Dealer table starts at row 23
    start_dealer_row = 23
    for r_idx, r_data in enumerate(dealer_rows):
        target_row = start_dealer_row + r_idx
        for c_idx, cell_data in enumerate(r_data, start=1):
            c = ws.cell(row=target_row, column=c_idx)
            c.value = cell_data['value']
            if cell_data['font']: c.font = copy(cell_data['font'])
            if cell_data['fill']: c.fill = copy(cell_data['fill'])
            if cell_data['alignment']: c.alignment = copy(cell_data['alignment'])
            if cell_data['border']: c.border = copy(cell_data['border'])
            if cell_data['number_format']: c.number_format = cell_data['number_format']
            if cell_data['hyperlink']: c.hyperlink = copy(cell_data['hyperlink'])

    # Set column widths
    widths = {
        'A': 16.0,  # Марка / Город
        'B': 22.0,  # Модель / Ссылка на группу
        'C': 42.0,  # Комплектация / Название
        'D': 25.0,  # Год / ЮЛ
        'E': 16.0,  # РРЦ / ИНН
        'F': 16.0,  # Скидка клиенту / Код ФДЦ
        'G': 18.0,  # Цена для клиента / Адрес
        'H': 25.0,  # Название в беке
        'I': 45.0,  # Почты для передачи лидов
        'J': 20.0,  # Ответственный
        'K': 20.0,  # График
        'L': 15.0,  # Разница с МСК
        'M': 12.0,  # карта
    }
    for col_letter, width in widths.items():
        ws.column_dimensions[col_letter].width = width

    # Save workbook
    wb.save(FILE_PATH)
    print(f'Successfully updated {FILE_PATH} sheet {sheet_name}')

if __name__ == '__main__':
    update_moskvich()
