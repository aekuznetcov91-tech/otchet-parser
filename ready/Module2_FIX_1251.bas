Attribute VB_Name = "Module2"
Public Sub ImportAllData()
    Dim wbMain As Workbook, wbSource As Workbook
    Dim wsRaw As Worksheet, wsDict As Worksheet, wsLeads As Worksheet
    Dim fd As FileDialog
    Dim fileRaw As String, fileDict As String, fileLeads As String

    Set wbMain = ActiveWorkbook

    ' ==========================================
    ' 1. ЗАГРУЗКА СЫРОЙ ВЫГРУЗКИ
    ' ==========================================
    If MsgBox("Загрузить файл с СЫРОЙ ВЫГРУЗКОЙ?", vbYesNo + vbQuestion, "Шаг 1 из 3") = vbYes Then
        Set fd = Application.FileDialog(msoFileDialogFilePicker)
        With fd
            .Title = "Выберите файл с СЫРОЙ ВЫГРУЗКОЙ"
            .Filters.Clear
            .Filters.Add "Excel Files", "*.xls*"
            .AllowMultiSelect = False
            If .Show = -1 Then fileRaw = .SelectedItems(1)
        End With

        If fileRaw <> "" Then
            Application.ScreenUpdating = False
            Application.DisplayAlerts = False

            On Error Resume Next
            Set wsRaw = wbMain.Sheets("Сырые данные")
            On Error GoTo 0
            If wsRaw Is Nothing Then
                Set wsRaw = wbMain.Sheets.Add(Before:=wbMain.Sheets(1))
                wsRaw.Name = "Сырые данные"
            End If

            wsRaw.Cells.Clear
            Set wbSource = Workbooks.Open(fileRaw)
            wbSource.Sheets(1).UsedRange.Copy Destination:=wsRaw.Range("A1")
            wbSource.Close SaveChanges:=False

            Application.DisplayAlerts = True
            Application.ScreenUpdating = True
        End If
    End If

    ' ==========================================
    ' 2. ЗАГРУЗКА СПРАВОЧНИКА ПАРТНЕРОВ
    ' ==========================================
    If MsgBox("Загрузить файл 'Справочник партнеры'?", vbYesNo + vbQuestion, "Шаг 2 из 3") = vbYes Then
        Set fd = Application.FileDialog(msoFileDialogFilePicker)
        With fd
            .Title = "Выберите файл со СПРАВОЧНИКОМ ПАРТНЕРОВ"
            .Filters.Clear
            .Filters.Add "Excel Files", "*.xls*"
            .AllowMultiSelect = False
            If .Show = -1 Then fileDict = .SelectedItems(1)
        End With

        If fileDict <> "" Then
            Application.ScreenUpdating = False
            Application.DisplayAlerts = False

            On Error Resume Next
            Set wsDict = wbMain.Sheets("Справочник партнеры")
            On Error GoTo 0
            If wsDict Is Nothing Then
                Set wsDict = wbMain.Sheets.Add(After:=wbMain.Sheets(wbMain.Sheets.Count))
                wsDict.Name = "Справочник партнеры"
            End If

            wsDict.Cells.Clear
            Set wbSource = Workbooks.Open(fileDict)
            wbSource.Sheets(1).UsedRange.Copy Destination:=wsDict.Range("A1")
            wbSource.Close SaveChanges:=False

            Application.DisplayAlerts = True
            Application.ScreenUpdating = True
        End If
    End If

    ' ==========================================
    ' 3. ЗАГРУЗКА ВЫГРУЗКИ ЛИДОВ
    ' ==========================================
    If MsgBox("Загрузить файл 'Лиды'?", vbYesNo + vbQuestion, "Шаг 3 из 3") = vbYes Then
        Set fd = Application.FileDialog(msoFileDialogFilePicker)
        With fd
            .Title = "Выберите файл с ЛИДАМИ"
            .Filters.Clear
            .Filters.Add "Excel Files", "*.xls*"
            .AllowMultiSelect = False
            If .Show = -1 Then fileLeads = .SelectedItems(1)
        End With

        If fileLeads <> "" Then
            Application.ScreenUpdating = False
            Application.DisplayAlerts = False

            On Error Resume Next
            Set wsLeads = wbMain.Sheets("лиды")
            On Error GoTo 0
            If wsLeads Is Nothing Then
                Set wsLeads = wbMain.Sheets.Add(After:=wbMain.Sheets(wbMain.Sheets.Count))
                wsLeads.Name = "лиды"
            End If

            wsLeads.Cells.Clear
            Set wbSource = Workbooks.Open(fileLeads)
            wbSource.Sheets(1).UsedRange.Copy Destination:=wsLeads.Range("A1")
            wbSource.Close SaveChanges:=False

            Application.DisplayAlerts = True
            Application.ScreenUpdating = True
        End If
    End If

    If Not wsRaw Is Nothing Then wsRaw.Activate
    MsgBox "Все внешние файлы успешно загружены в эту книгу!", vbInformation, "Успех"
End Sub
