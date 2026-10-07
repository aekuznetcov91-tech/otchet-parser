import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_JSON_PATH = os.path.join(PROJECT_ROOT, 'data.json')
OUTPUT_XLSX_PATH = os.path.join(PROJECT_ROOT, 'Отчет_по_передачам_лидов_Q3_2026.xlsx')

def main():
    with open(DATA_JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sys_partners = data.get('sys_db_partners', [])

    months = [
        ('2026-07', 'Июль 2026'),
        ('2026-08', 'Август 2026'),
        ('2026-09', 'Сентябрь 2026')
    ]

    companies = [
        {
            'name': 'АвтоГермес',
            'pids': [1098],
            'holding': 'ГК АвтоГермес',
            'kam': 'Андрей Кузнецов'
        },
        {
            'name': 'У Сервис',
            'pids': [1111, 1143],
            'holding': 'ГК У Сервис+',
            'kam': 'Алексей Чихарев'
        },
        {
            'name': 'Кунцево',
            'pids': [1091],
            'holding': 'ТЦ Кунцево',
            'kam': 'Алексей Чихарев'
        },
        {
            'name': 'Авилон',
            'pids': [632046],
            'holding': 'Авилон АГ',
            'kam': 'Алексей Чихарев'
        }
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Сводный отчет Q3 2026'

    # Enable grid lines
    ws.views.sheetView[0].showGridLines = True

    # Styling definitions
    font_title = Font(name='Segoe UI', size=16, bold=True, color='1E3A8A')
    font_subtitle = Font(name='Segoe UI', size=10, italic=True, color='4B5563')
    font_header = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
    font_company_hdr = Font(name='Segoe UI', size=11, bold=True, color='1E3A8A')
    font_regular = Font(name='Segoe UI', size=10, color='1F2937')
    font_bold = Font(name='Segoe UI', size=10, bold=True, color='111827')
    font_grand_total = Font(name='Segoe UI', size=11, bold=True, color='1E3A8A')

    fill_header = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
    fill_company_hdr = PatternFill(start_color='F3F4F6', end_color='F3F4F6', fill_type='solid')
    fill_subtotal = PatternFill(start_color='EEF2FF', end_color='EEF2FF', fill_type='solid')
    fill_grand_total = PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid')
    fill_zebra = PatternFill(start_color='F9FAFB', end_color='F9FAFB', fill_type='solid')

    border_thin = Side(border_style='thin', color='D1D5DB')
    border_thick_top = Side(border_style='thin', color='9CA3AF')
    border_double_bottom = Side(border_style='double', color='1E3A8A')

    box_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)
    subtotal_border = Border(left=border_thin, right=border_thin, top=border_thick_top, bottom=border_thin)
    grand_total_border = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_double_bottom)

    align_left = Alignment(horizontal='left', vertical='center')
    align_center = Alignment(horizontal='center', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')
    align_header = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 1. Document Title block
    ws.merge_cells('A1:G1')
    ws['A1'] = 'Отчет по передачам лидов и воронке Trade-in (Июль – Сентябрь 2026)'
    ws['A1'].font = font_title
    ws['A1'].alignment = align_left
    ws.row_dimensions[1].height = 28

    ws.merge_cells('A2:G2')
    ws['A2'] = 'Компании: АвтоГермес, У Сервис, ТЦ Кунцево, Авилон | Формат: чистые лиды CRM + сделки ФДЦ и Онлайн | Воронка ТИ: 85% и 55%'
    ws['A2'].font = font_subtitle
    ws['A2'].alignment = align_left
    ws.row_dimensions[2].height = 18

    ws.row_dimensions[3].height = 10  # blank spacer row

    # 2. Table Headers
    headers = [
        'Компания (Холдинг)',
        'Период',
        'Передано лидов\n(CRM + ФДЦ/Онлайн)',
        'Клиентов с ТИ\n(85% от переданных)',
        'Готовы пойти в ТИ\n(55% от клиентов ТИ)',
        'Сделки с передачи\n(чистые из лидов)',
        'Сквозной CR\n(Сделки / Лиды)'
    ]

    header_row = 4
    ws.row_dimensions[header_row].height = 36

    for col_idx, h_text in enumerate(headers, 1):
        cell = ws.cell(row=header_row, column=col_idx, value=h_text)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_header
        cell.border = box_border

    current_row = 5
    company_subtotal_rows = []

    # 3. Data population per company
    for comp in companies:
        c_name = comp['name']
        pids = comp['pids']
        comp_start_row = current_row

        for m_idx, (m_code, m_title) in enumerate(months):
            recs = [r for r in sys_partners if r.get('PartnerId') in pids and r.get('Month') == m_code]

            # 1. Leads
            crm_leads = sum(r.get('Qty', 1) for r in recs if r.get('Type') == 'Лид' and not r.get('HasPrepay'))

            # 2. Deals
            deals = [r for r in recs if r.get('Type') == 'Сделка']
            fdc_online = sum(r.get('Qty', 1) for r in deals if any(k in (r.get('B2C') or '').upper() for k in ['ФДЦ', 'ONLINE', 'ОНЛАЙН']))

            # Combined transferred leads
            tot_trans_leads = crm_leads + fdc_online

            # 3. Pure lead transfers
            pure_trans_deals = sum(r.get('Qty', 1) for r in deals if (r.get('IsLeadSaleNoPrepay') == 1 or 'ПЕРЕДАЧА' in (r.get('B2C') or '').upper()) and not any(k in (r.get('B2C') or '').upper() for k in ['МП1', 'МП2', 'МП3', 'MP', 'ФДЦ', 'ONLINE', 'ОНЛАЙН']))

            ws.row_dimensions[current_row].height = 22

            # Company name
            c_cell = ws.cell(row=current_row, column=1, value=c_name if m_idx == 0 else '')
            c_cell.font = font_bold if m_idx == 0 else font_regular
            c_cell.alignment = align_left
            c_cell.border = box_border

            # Period
            p_cell = ws.cell(row=current_row, column=2, value=m_title)
            p_cell.font = font_regular
            p_cell.alignment = align_center
            p_cell.border = box_border

            # Transferred leads
            l_cell = ws.cell(row=current_row, column=3, value=tot_trans_leads)
            l_cell.font = font_regular
            l_cell.alignment = align_right
            l_cell.number_format = '#,##0'
            l_cell.border = box_border

            # Clients with TI (85%)
            ti_cell = ws.cell(row=current_row, column=4, value=f'=C{current_row}*0.85')
            ti_cell.font = font_regular
            ti_cell.alignment = align_right
            ti_cell.number_format = '#,##0.0'
            ti_cell.border = box_border

            # Ready for TI (55%)
            ready_cell = ws.cell(row=current_row, column=5, value=f'=D{current_row}*0.55')
            ready_cell.font = font_regular
            ready_cell.alignment = align_right
            ready_cell.number_format = '#,##0.0'
            ready_cell.border = box_border

            # Deals from lead transfers
            d_cell = ws.cell(row=current_row, column=6, value=pure_trans_deals)
            d_cell.font = font_regular
            d_cell.alignment = align_right
            d_cell.number_format = '#,##0'
            d_cell.border = box_border

            # Conversion rate CR (%)
            cr_cell = ws.cell(row=current_row, column=7, value=f'=IF(C{current_row}>0, F{current_row}/C{current_row}, 0)')
            cr_cell.font = font_bold if pure_trans_deals > 0 else font_regular
            cr_cell.alignment = align_right
            cr_cell.number_format = '0.0%'
            cr_cell.border = box_border

            if m_idx % 2 == 1:
                for col in range(1, 8):
                    ws.cell(row=current_row, column=col).fill = fill_zebra

            current_row += 1

        comp_end_row = current_row - 1

        # Company subtotal row
        ws.row_dimensions[current_row].height = 24
        sub_c_cell = ws.cell(row=current_row, column=1, value=f'Итого {c_name}')
        sub_c_cell.font = font_bold
        sub_c_cell.alignment = align_left

        sub_p_cell = ws.cell(row=current_row, column=2, value='3 месяца (Q3)')
        sub_p_cell.font = font_bold
        sub_p_cell.alignment = align_center

        sub_l_cell = ws.cell(row=current_row, column=3, value=f'=SUM(C{comp_start_row}:C{comp_end_row})')
        sub_l_cell.font = font_bold
        sub_l_cell.alignment = align_right
        sub_l_cell.number_format = '#,##0'

        sub_ti_cell = ws.cell(row=current_row, column=4, value=f'=C{current_row}*0.85')
        sub_ti_cell.font = font_bold
        sub_ti_cell.alignment = align_right
        sub_ti_cell.number_format = '#,##0.0'

        sub_ready_cell = ws.cell(row=current_row, column=5, value=f'=D{current_row}*0.55')
        sub_ready_cell.font = font_bold
        sub_ready_cell.alignment = align_right
        sub_ready_cell.number_format = '#,##0.0'

        sub_d_cell = ws.cell(row=current_row, column=6, value=f'=SUM(F{comp_start_row}:F{comp_end_row})')
        sub_d_cell.font = font_bold
        sub_d_cell.alignment = align_right
        sub_d_cell.number_format = '#,##0'

        sub_cr_cell = ws.cell(row=current_row, column=7, value=f'=IF(C{current_row}>0, F{current_row}/C{current_row}, 0)')
        sub_cr_cell.font = font_bold
        sub_cr_cell.alignment = align_right
        sub_cr_cell.number_format = '0.0%'

        for col in range(1, 8):
            cell = ws.cell(row=current_row, column=col)
            cell.fill = fill_subtotal
            cell.border = subtotal_border

        company_subtotal_rows.append(current_row)
        current_row += 1

        # Spacer row between companies
        ws.row_dimensions[current_row].height = 10
        current_row += 1

    # 4. Summary block: ИТОГО ПО 4 КОМПАНИЯМ
    summary_title_row = current_row
    ws.merge_cells(start_row=summary_title_row, start_column=1, end_row=summary_title_row, end_column=7)
    s_title = ws.cell(row=summary_title_row, column=1, value='СВОДНЫЕ ИТОГИ ПО 4 ХОЛДИНГАМ')
    s_title.font = font_company_hdr
    s_title.fill = fill_company_hdr
    s_title.alignment = align_left
    ws.row_dimensions[summary_title_row].height = 24
    for col in range(1, 8):
        ws.cell(row=summary_title_row, column=col).border = box_border

    current_row += 1

    # Monthly totals across 4 companies
    month_summary_start = current_row
    for m_idx, (m_code, m_title) in enumerate(months):
        ws.row_dimensions[current_row].height = 22
        m_cells_l = [f'C{r}' for r in [5 + m_idx, 10 + m_idx, 15 + m_idx, 20 + m_idx]]
        m_cells_d = [f'F{r}' for r in [5 + m_idx, 10 + m_idx, 15 + m_idx, 20 + m_idx]]

        ws.cell(row=current_row, column=1, value='Все 4 компании').font = font_regular
        ws.cell(row=current_row, column=1).alignment = align_left
        ws.cell(row=current_row, column=1).border = box_border

        ws.cell(row=current_row, column=2, value=m_title).font = font_regular
        ws.cell(row=current_row, column=2).alignment = align_center
        ws.cell(row=current_row, column=2).border = box_border

        c_l = ws.cell(row=current_row, column=3, value=f'={"+".join(m_cells_l)}')
        c_l.font = font_regular
        c_l.alignment = align_right
        c_l.number_format = '#,##0'
        c_l.border = box_border

        c_ti = ws.cell(row=current_row, column=4, value=f'=C{current_row}*0.85')
        c_ti.font = font_regular
        c_ti.alignment = align_right
        c_ti.number_format = '#,##0.0'
        c_ti.border = box_border

        c_ready = ws.cell(row=current_row, column=5, value=f'=D{current_row}*0.55')
        c_ready.font = font_regular
        c_ready.alignment = align_right
        c_ready.number_format = '#,##0.0'
        c_ready.border = box_border

        c_d = ws.cell(row=current_row, column=6, value=f'={"+".join(m_cells_d)}')
        c_d.font = font_regular
        c_d.alignment = align_right
        c_d.number_format = '#,##0'
        c_d.border = box_border

        c_cr = ws.cell(row=current_row, column=7, value=f'=IF(C{current_row}>0, F{current_row}/C{current_row}, 0)')
        c_cr.font = font_bold
        c_cr.alignment = align_right
        c_cr.number_format = '0.0%'
        c_cr.border = box_border

        if m_idx % 2 == 1:
            for col in range(1, 8):
                ws.cell(row=current_row, column=col).fill = fill_zebra

        current_row += 1

    month_summary_end = current_row - 1

    # Grand total row
    ws.row_dimensions[current_row].height = 26
    tot_c = ws.cell(row=current_row, column=1, value='ИТОГО ВСЕ ХОЛДИНГИ')
    tot_c.font = font_grand_total
    tot_c.alignment = align_left

    tot_p = ws.cell(row=current_row, column=2, value='ИТОГО ЗА 3 МЕСЯЦА')
    tot_p.font = font_grand_total
    tot_p.alignment = align_center

    tot_l = ws.cell(row=current_row, column=3, value=f'=SUM(C{month_summary_start}:C{month_summary_end})')
    tot_l.font = font_grand_total
    tot_l.alignment = align_right
    tot_l.number_format = '#,##0'

    tot_ti = ws.cell(row=current_row, column=4, value=f'=C{current_row}*0.85')
    tot_ti.font = font_grand_total
    tot_ti.alignment = align_right
    tot_ti.number_format = '#,##0.0'

    tot_ready = ws.cell(row=current_row, column=5, value=f'=D{current_row}*0.55')
    tot_ready.font = font_grand_total
    tot_ready.alignment = align_right
    tot_ready.number_format = '#,##0.0'

    tot_d = ws.cell(row=current_row, column=6, value=f'=SUM(F{month_summary_start}:F{month_summary_end})')
    tot_d.font = font_grand_total
    tot_d.alignment = align_right
    tot_d.number_format = '#,##0'

    tot_cr = ws.cell(row=current_row, column=7, value=f'=IF(C{current_row}>0, F{current_row}/C{current_row}, 0)')
    tot_cr.font = font_grand_total
    tot_cr.alignment = align_right
    tot_cr.number_format = '0.0%'

    for col in range(1, 8):
        cell = ws.cell(row=current_row, column=col)
        cell.fill = fill_grand_total
        cell.border = grand_total_border

    # 5. Column width auto-fit
    min_widths = {
        1: 24, # Компания
        2: 20, # Период
        3: 24, # Передано лидов
        4: 22, # Клиентов с ТИ
        5: 22, # Готовы пойти в ТИ
        6: 22, # Сделки с передачи
        7: 18  # Сквозной CR
    }

    for col_idx in range(1, 8):
        col_letter = get_column_letter(col_idx)
        ws.column_dimensions[col_letter].width = min_widths.get(col_idx, 20)

    # 6. Save workbook
    wb.save(OUTPUT_XLSX_PATH)
    print(f'Отчет успешно создан: {OUTPUT_XLSX_PATH}')

if __name__ == '__main__':
    main()
