Attribute VB_Name = "Module1"
Public GlobalBrandSplits As Object
Public GlobalTotalSplits As Object

Public Sub CreateSalesSplitReport_Ultimate_Final_v46()
    Dim wsRaw As Worksheet
    Dim wsLeads As Worksheet

    ' 1. Smart sheet search: first try "Сырые данные", else use active
    On Error Resume Next
    Set wsRaw = ActiveWorkbook.Sheets("Сырые данные")
    On Error GoTo ErrorHandler

    If wsRaw Is Nothing Then
        Set wsRaw = ActiveSheet
    End If

    ' Fool-proof check: skip system sheets
    If wsRaw.Name = "Диаграмма" Or wsRaw.Name = "Динамика" Or wsRaw.Name = "Динамика месяцы" Or _
       wsRaw.Name = "Менеджеры" Or wsRaw.Name = "SYS_DB" Or wsRaw.Name = "Справочник партнеры" Or _
       wsRaw.Name = "лиды" Or wsRaw.Name = "Воронка КАМ" Or wsRaw.Name = "Партнеры" Or wsRaw.Name = "SYS_DB_PARTNERS" Then
        MsgBox "Пожалуйста, перейдите на лист с сырой выгрузкой (или загрузите данные через импорт)!", vbCritical, "Ошибка"
        Exit Sub
    End If

    ' --- SPEED OPTIMIZATION ---
    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual
    Application.EnableEvents = False

    On Error GoTo ErrorHandler

    Set wsLeads = Nothing
    On Error Resume Next
    Set wsLeads = ActiveWorkbook.Sheets("лиды")
    On Error GoTo ErrorHandler

    If wsLeads Is Nothing Then
        Call CoreReportLogic(wsRaw)
        Call Report_Partners_Summary(wsRaw)
    Else
        Call UpdatePartnersDirectory(wsRaw, wsLeads)
        If MsgBox("Справочник партнеров проверен/обновлен!" & vbCrLf & vbCrLf & "Продолжить построение отчета?", vbYesNo + vbQuestion, "Справочник") = vbYes Then
            Call CoreReportLogic(wsRaw)
            Call Report_Partners_Summary(wsRaw)
        Else
            GoTo ExitRoutine
        End If
    End If

    ActiveWorkbook.Sheets("Диаграмма").Activate
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    MsgBox "Готово! Основные дашборды и динамика успешно собраны.", vbInformation, "Успех"
    Exit Sub

ErrorHandler:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
    MsgBox "Произошла ошибка: " & Err.Description, vbCritical
ExitRoutine:
    Application.Calculation = xlCalculationAutomatic
    Application.EnableEvents = True
    Application.ScreenUpdating = True
End Sub

Public Sub RefreshWeeklyView()
    Dim ws As Worksheet
    Dim rFind As Range
    Dim wR As Long
    Dim c As Long

    Set ws = ActiveSheet
    If ws.Name <> "Динамика месяцы" Then Exit Sub

    ws.Calculate

    Set rFind = ws.Range("A:A").Find("ПОНЕДЕЛЬНОЕ СРАВНЕНИЕ")
    If Not rFind Is Nothing Then
        wR = rFind.Row + 1
        Application.ScreenUpdating = False
        For c = 2 To 200
            If InStr(1, ws.Cells(wR, c).Formula, "Неделя") > 0 Then
                If ws.Cells(wR, c).Value = "" Then
                    ws.Columns(c).Hidden = True
                Else
                    ws.Columns(c).Hidden = False
                    ws.Columns(c).AutoFit
                End If
            End If
        Next c
        Application.ScreenUpdating = True
    End If
End Sub

Public Function ParseDateCustom(ByVal s As String) As Date
    Dim cleanStr As String
    Dim p() As String

    On Error Resume Next
    ParseDateCustom = DateSerial(1900, 1, 1)
    If s = "" Then Exit Function
    If IsDate(s) Then
        ParseDateCustom = CDate(s)
        Exit Function
    End If

    cleanStr = Trim(Split(s, " ")(0))
    If InStr(cleanStr, ".") > 0 Then p = Split(cleanStr, ".")
    If InStr(cleanStr, "-") > 0 Then p = Split(cleanStr, "-")
    If InStr(cleanStr, "/") > 0 Then p = Split(cleanStr, "/")

    On Error Resume Next
    If (Not Not p) <> 0 Then
        If UBound(p) = 2 Then
            If Len(p(0)) = 4 Then
                ParseDateCustom = DateSerial(CInt(p(0)), CInt(p(1)), CInt(p(2)))
            Else
                ParseDateCustom = DateSerial(CInt(p(2)), CInt(p(1)), CInt(p(0)))
            End If
        End If
    End If
    On Error GoTo 0
End Function

Public Function CleanTextString(ByVal s As String) As String
    s = UCase(Trim(CStr(s)))
    s = Replace(s, Chr(160), " ")
    s = Replace(s, """", "")
    s = Replace(s, "<<", "")
    s = Replace(s, ">>", "")
    s = Replace(s, "'", "")
    Do While InStr(s, "  ") > 0
        s = Replace(s, "  ", " ")
    Loop
    CleanTextString = Trim(s)
End Function

Public Function CleanID(ByVal id As Variant) As String
    Dim s As String
    s = CStr(id)

    s = Replace(s, Chr(160), "")
    s = Replace(s, Chr(10), "")
    s = Replace(s, Chr(13), "")
    s = Replace(s, Chr(9), "")
    s = Replace(s, " ", "")
    s = Trim(s)

    If Right(s, 2) = ".0" Then s = Left(s, Len(s) - 2)
    If Right(s, 3) = ".00" Then s = Left(s, Len(s) - 3)

    On Error Resume Next
    If IsNumeric(s) And Len(s) > 0 Then
        If InStr(UCase(s), "E") = 0 Then
            s = CStr(CDec(s))
        End If
    End If
    On Error GoTo 0

    CleanID = UCase(s)
End Function

Public Sub BuildBrandSplitsCache()
    Set GlobalBrandSplits = CreateObject("Scripting.Dictionary")
    Set GlobalTotalSplits = CreateObject("Scripting.Dictionary")

    Dim wsSysPart As Worksheet
    Dim lr As Long
    Dim arr As Variant
    Dim dictM As Object
    Dim dictT As Object
    Dim r As Long
    Dim pName As String
    Dim period As String
    Dim br As String
    Dim key As String

    On Error Resume Next
    Set wsSysPart = ActiveWorkbook.Sheets("SYS_DB_PARTNERS")
    On Error GoTo 0

    If wsSysPart Is Nothing Then Exit Sub

    lr = wsSysPart.Cells(wsSysPart.Rows.Count, 1).End(xlUp).Row
    If lr < 2 Then Exit Sub

    arr = wsSysPart.Range("A1:G" & lr).Value
    Set dictM = CreateObject("Scripting.Dictionary")
    Set dictT = CreateObject("Scripting.Dictionary")

    For r = 2 To UBound(arr)
        If arr(r, 1) = "Сделка" Then
            pName = UCase(Trim(CStr(arr(r, 3))))
            period = Trim(CStr(arr(r, 2)))
            br = Trim(CStr(arr(r, 7)))

            If br <> "" Then
                key = pName & "|" & period
                If Not dictM.Exists(key) Then
                    Set dictM(key) = CreateObject("Scripting.Dictionary")
                End If
                dictM(key)(br) = dictM(key)(br) + 1

                key = pName & "|All time"
                If Not dictM.Exists(key) Then
                    Set dictM(key) = CreateObject("Scripting.Dictionary")
                End If
                dictM(key)(br) = dictM(key)(br) + 1

                If Not dictT.Exists(period) Then
                    Set dictT(period) = CreateObject("Scripting.Dictionary")
                End If
                dictT(period)(br) = dictT(period)(br) + 1

                If Not dictT.Exists("Весь период") Then
                    Set dictT("Весь период") = CreateObject("Scripting.Dictionary")
                End If
                dictT("Весь период")(br) = dictT("Весь период")(br) + 1
            End If
        End If
    Next r

    Dim k As Variant
    Dim b As Variant
    Dim res As String

    For Each k In dictM.Keys
        res = ""
        For Each b In dictM(k).Keys
            res = res & b & " (" & dictM(k)(b) & " шт), "
        Next b
        If Len(res) > 2 Then
            res = Left(res, Len(res) - 2)
        End If
        GlobalBrandSplits(CStr(k)) = res
    Next k

    For Each k In dictT.Keys
        res = ""
        For Each b In dictT(k).Keys
            res = res & b & " " & dictT(k)(b) & " шт. | "
        Next b
        If Len(res) > 3 Then
            res = Left(res, Len(res) - 3)
        End If
        GlobalTotalSplits(CStr(k)) = res
    Next k
End Sub

Public Function GetPartnerBrandSplit(pName As String, period As String) As String
    Application.Volatile
    If GlobalBrandSplits Is Nothing Then
        Call BuildBrandSplitsCache
    End If

    Dim key As String
    key = UCase(Trim(pName)) & "|" & period

    If GlobalBrandSplits.Exists(key) Then
        GetPartnerBrandSplit = GlobalBrandSplits(key)
    Else
        GetPartnerBrandSplit = ""
    End If
End Function

Public Function GetTotalBrandSplit(period As String) As String
    Application.Volatile
    If GlobalTotalSplits Is Nothing Then
        Call BuildBrandSplitsCache
    End If

    If GlobalTotalSplits.Exists(period) Then
        GetTotalBrandSplit = GlobalTotalSplits(period)
    Else
        GetTotalBrandSplit = "Нет данных"
    End If
End Function

Public Sub UpdatePartnersDirectory(wsRaw As Worksheet, wsLeads As Worksheet)
    Dim wsDict As Worksheet
    Dim colCompany As Long
    Dim colEvent As Long
    Dim colPartner As Long
    Dim c As Long
    Dim i As Long
    Dim hName As String
    Dim b As String
    Dim bi As String
    Dim kam As String
    Dim bKey As String
    Dim biKey As String
    Dim dMain As Object
    Dim dStandAloneBI As Object
    Dim lastRowDict As Long
    Dim lrRaw As Long
    Dim lrLeads As Long
    Dim isLinked As Boolean
    Dim k As Variant
    Dim totalItems As Long
    Dim arrOut() As Variant
    Dim rIdx As Long
    Dim isBiF As Boolean
    Dim isKamF As Boolean
    Dim iSort As Long
    Dim jSort As Long
    Dim temp1 As Variant
    Dim temp2 As Variant
    Dim temp3 As Variant
    Dim temp4 As Variant

    Set dMain = CreateObject("Scripting.Dictionary")
    Set dStandAloneBI = CreateObject("Scripting.Dictionary")

    For c = 1 To wsRaw.Cells(1, wsRaw.Columns.Count).End(xlToLeft).Column
        If UCase(Trim(wsRaw.Cells(1, c).Value)) = "КОМПАНИЯ" Then colCompany = c
    Next c
    For c = 1 To wsLeads.Cells(1, wsLeads.Columns.Count).End(xlToLeft).Column
        hName = UCase(Trim(wsLeads.Cells(1, c).Value))
        If hName = "EVENT_NAME" Then colEvent = c
        If hName = "PARTNER" Then colPartner = c
    Next c

    On Error Resume Next
    Set wsDict = ActiveWorkbook.Sheets("Справочник партнеры")
    On Error GoTo 0

    If wsDict Is Nothing Then
        Set wsDict = ActiveWorkbook.Sheets.Add(After:=wsRaw)
        wsDict.Name = "Справочник партнеры"
        wsDict.Cells(1, 1).Value = "Битрикс"
        wsDict.Cells(1, 2).Value = "BI"
        wsDict.Cells(1, 3).Value = "КАМ"
        wsDict.Range("A1:C1").Font.Bold = True
        wsDict.Range("A1:C1").Interior.Color = RGB(54, 96, 146)
        wsDict.Range("A1:C1").Font.Color = RGB(255, 255, 255)
    End If

    lastRowDict = wsDict.Cells(wsDict.Rows.Count, 1).End(xlUp).Row
    If wsDict.Cells(wsDict.Rows.Count, 2).End(xlUp).Row > lastRowDict Then
        lastRowDict = wsDict.Cells(wsDict.Rows.Count, 2).End(xlUp).Row
    End If

    For i = 2 To lastRowDict
        b = Trim(CStr(wsDict.Cells(i, 1).Value))
        bi = Trim(CStr(wsDict.Cells(i, 2).Value))
        kam = Trim(CStr(wsDict.Cells(i, 3).Value))

        If b <> "" Then
            bKey = CleanTextString(b)
            If Not dMain.Exists(bKey) Then
                dMain.Add bKey, Array(b, bi, kam)
            End If
        ElseIf bi <> "" Then
            biKey = CleanTextString(bi)
            If Not dStandAloneBI.Exists(biKey) Then
                dStandAloneBI.Add biKey, bi
            End If
        End If
    Next i

    If colCompany > 0 Then
        lrRaw = wsRaw.Cells(wsRaw.Rows.Count, colCompany).End(xlUp).Row
        For i = 2 To lrRaw
            b = Trim(CStr(wsRaw.Cells(i, colCompany).Value))
            If b <> "" Then
                bKey = CleanTextString(b)
                If Not dMain.Exists(bKey) Then
                    dMain.Add bKey, Array(b, "", "")
                End If
            End If
        Next i
    End If

    If colEvent > 0 And colPartner > 0 Then
        lrLeads = wsLeads.Cells(wsLeads.Rows.Count, colEvent).End(xlUp).Row
        For i = 2 To lrLeads
            If UCase(Trim(CStr(wsLeads.Cells(i, colEvent).Value))) = "ОТПРАВКА ЛИДА" Then
                bi = Trim(CStr(wsLeads.Cells(i, colPartner).Value))
                If bi <> "" Then
                    biKey = CleanTextString(bi)
                    isLinked = False
                    For Each k In dMain.Keys
                        If CleanTextString(CStr(dMain(k)(1))) = biKey Then
                            isLinked = True
                            Exit For
                        End If
                    Next k

                    If Not isLinked Then
                        If Not dStandAloneBI.Exists(biKey) Then
                            dStandAloneBI.Add biKey, bi
                        End If
                    End If
                End If
            End If
        Next i
    End If

    totalItems = dMain.Count + dStandAloneBI.Count
    If totalItems = 0 Then Exit Sub
    ReDim arrOut(1 To totalItems, 1 To 4)
    rIdx = 1

    For Each k In dMain.Keys
        arrOut(rIdx, 1) = dMain(k)(0)
        arrOut(rIdx, 2) = dMain(k)(1)
        arrOut(rIdx, 3) = dMain(k)(2)

        isBiF = (Trim(CStr(arrOut(rIdx, 2))) <> "")
        isKamF = (Trim(CStr(arrOut(rIdx, 3))) <> "")

        If isBiF And isKamF Then
            arrOut(rIdx, 4) = 1
        Else
            arrOut(rIdx, 4) = 2
        End If
        rIdx = rIdx + 1
    Next k

    For Each k In dStandAloneBI.Keys
        arrOut(rIdx, 1) = ""
        arrOut(rIdx, 2) = dStandAloneBI(k)
        arrOut(rIdx, 3) = ""
        arrOut(rIdx, 4) = 3
        rIdx = rIdx + 1
    Next k

    For iSort = 1 To totalItems - 1
        For jSort = iSort + 1 To totalItems
            If arrOut(iSort, 4) > arrOut(jSort, 4) Then
                temp1 = arrOut(iSort, 1)
                arrOut(iSort, 1) = arrOut(jSort, 1)
                arrOut(jSort, 1) = temp1

                temp2 = arrOut(iSort, 2)
                arrOut(iSort, 2) = arrOut(jSort, 2)
                arrOut(jSort, 2) = temp2

                temp3 = arrOut(iSort, 3)
                arrOut(iSort, 3) = arrOut(jSort, 3)
                arrOut(jSort, 3) = temp3

                temp4 = arrOut(iSort, 4)
                arrOut(iSort, 4) = arrOut(jSort, 4)
                arrOut(jSort, 4) = temp4
            End If
        Next jSort
    Next iSort

    wsDict.Range("A2:C" & wsDict.Rows.Count).Clear
    Application.ScreenUpdating = False

    For i = 1 To totalItems
        wsDict.Cells(i + 1, 1).Value = arrOut(i, 1)
        wsDict.Cells(i + 1, 2).Value = arrOut(i, 2)
        wsDict.Cells(i + 1, 3).Value = arrOut(i, 3)
        If arrOut(i, 4) = 1 Then
            wsDict.Range(wsDict.Cells(i + 1, 1), wsDict.Cells(i + 1, 3)).Interior.ColorIndex = xlNone
        Else
            wsDict.Range(wsDict.Cells(i + 1, 1), wsDict.Cells(i + 1, 3)).Interior.Color = RGB(255, 255, 0)
        End If
    Next i

    wsDict.Columns("A:C").AutoFit
    Application.ScreenUpdating = True
End Sub

Public Sub Report_Partners_Summary(wsRaw As Worksheet)
    Dim wsPart As Worksheet
    Dim wsSys As Worksheet
    Dim wsSysPart As Worksheet
    Dim wsLeads As Worksheet
    Dim wsDict As Worksheet
    Dim r As Long
    Dim lr As Long
    Dim cCount As Long
    Dim bCount As Long
    Dim noSCount As Long
    Dim i As Long
    Dim c As Long
    Dim dictSales As Object
    Dim dictAllBI As Object
    Dim dictBI_to_Bitrix As Object
    Dim dictBI_AllTimeLeads As Object
    Dim dictB2C As Object
    Dim dictBitrix_to_KAM As Object
    Dim dictBI_to_KAM As Object
    Dim dictBitrixOrigName As Object
    Dim k As Variant
    Dim iSort As Long
    Dim jSort As Long
    Dim tempN As Long
    Dim tempS As String
    Dim arrCompSorted() As String
    Dim arrSalesSorted() As Long
    Dim b2cNames() As String
    Dim compU2 As String
    Dim compDisplay As String
    Dim kName As String
    Dim colLetter As String
    Dim colTotal As Long
    Dim colPrepay As Long
    Dim colWait As Long
    Dim colBrandSplit As Long
    Dim hName As String
    Dim dColB As Long
    Dim dColBI As Long
    Dim dColK As Long
    Dim dLr As Long
    Dim bName As String
    Dim biName As String
    Dim kamName As String
    Dim comp As String
    Dim b2c As String
    Dim pType As String
    Dim idxLocal As Long
    Dim r2 As Long
    Dim startR2 As Long
    Dim biNameStr As String
    Dim biNameU As String
    Dim bitrixRef As String
    Dim addToTable2 As Boolean
    Dim arrNoSComp() As String
    Dim arrNoSLeads() As Long
    Dim cNoBI As String
    Dim colLClient As Long
    Dim colLPartner As Long
    Dim colLDate As Long
    Dim lLr As Long
    Dim lPartRaw As String
    Dim lPartU As String

    On Error Resume Next
    Set wsSys = ActiveWorkbook.Sheets("SYS_DB")
    Set wsSysPart = ActiveWorkbook.Sheets("SYS_DB_PARTNERS")
    Set wsDict = ActiveWorkbook.Sheets("Справочник партнеры")
    On Error GoTo 0

    If wsSys Is Nothing Or wsSysPart Is Nothing Then Exit Sub

    Application.DisplayAlerts = False
    On Error Resume Next
    ActiveWorkbook.Sheets("Партнеры").Delete
    On Error GoTo 0
    Application.DisplayAlerts = True

    Set wsPart = ActiveWorkbook.Sheets.Add(After:=wsRaw)
    wsPart.Name = "Партнеры"
    wsPart.Cells(1, 1).Value = "ВЫБЕРИТЕ ПЕРИОД ДЛЯ АНАЛИЗА ПАРТНЕРОВ ->"
    wsPart.Cells(1, 1).Font.Bold = True

    Dim lastMRow As Long
    lastMRow = wsSys.Cells(wsSys.Rows.Count, 13).End(xlUp).Row
    With wsPart.Cells(1, 3)
        .NumberFormat = "@"
        .Value = Format(Date, "yyyy-mm")
        .Interior.Color = RGB(255, 255, 204)
        .Font.Bold = True
        .Borders.LineStyle = xlContinuous
        If lastMRow >= 1 Then
            .Validation.Delete
            .Validation.Add Type:=xlValidateList, Formula1:="=SYS_DB!$M$1:$M$" & lastMRow
        End If
    End With

    Set dictBitrix_to_KAM = CreateObject("Scripting.Dictionary")
    Set dictBI_to_KAM = CreateObject("Scripting.Dictionary")
    Set dictBI_to_Bitrix = CreateObject("Scripting.Dictionary")
    Set dictAllBI = CreateObject("Scripting.Dictionary")
    Set dictBitrixOrigName = CreateObject("Scripting.Dictionary")

    If Not wsDict Is Nothing Then
        dColB = 1
        dColBI = 2
        dColK = 3
        For c = 1 To wsDict.Cells(1, wsDict.Columns.Count).End(xlToLeft).Column
            hName = UCase(Trim(wsDict.Cells(1, c).Value))
            If hName = "БИТРИКС" Then dColB = c
            If hName = "BI" Then dColBI = c
            If hName = "КАМ" Then dColK = c
        Next c

        dLr = wsDict.Cells(wsDict.Rows.Count, dColB).End(xlUp).Row
        For i = 2 To dLr
            bName = Trim(CStr(wsDict.Cells(i, dColB).Value))
            biName = Trim(CStr(wsDict.Cells(i, dColBI).Value))
            kamName = Trim(CStr(wsDict.Cells(i, dColK).Value))
            If kamName = "" Then kamName = "Без КАМа"

            If bName <> "" Then
                dictBitrix_to_KAM(UCase(bName)) = kamName
                dictBitrixOrigName(UCase(bName)) = bName
            End If
            If biName <> "" Then
                dictAllBI(biName) = True
                dictBI_to_KAM(biName) = kamName
                If bName <> "" Then
                    dictBI_to_Bitrix(UCase(biName)) = UCase(bName)
                End If
            End If
        Next i
    End If

    Set dictSales = CreateObject("Scripting.Dictionary")
    Set dictB2C = CreateObject("Scripting.Dictionary")

    lr = wsSysPart.Cells(wsSysPart.Rows.Count, 3).End(xlUp).Row
    For r = 2 To lr
        comp = Trim(CStr(wsSysPart.Cells(r, 3).Value))
        b2c = Trim(CStr(wsSysPart.Cells(r, 4).Value))
        pType = Trim(CStr(wsSysPart.Cells(r, 1).Value))

        If b2c <> "" Then dictB2C(b2c) = True
        If comp <> "" Then
            If pType = "Сделка" Then
                dictSales(comp) = dictSales(comp) + 1
            End If
        End If
    Next r

    wsPart.Cells(3, 1).Value = "Компания"
    wsPart.Cells(3, 2).Value = "КАМ"
    wsPart.Cells(3, 3).Value = "Передачи"

    bCount = dictB2C.Count
    If bCount > 0 Then
        ReDim b2cNames(1 To bCount)
        idxLocal = 1
        For Each k In dictB2C.Keys
            b2cNames(idxLocal) = CStr(k)
            idxLocal = idxLocal + 1
        Next k
    Else
        bCount = 1
        ReDim b2cNames(1 To 1)
        b2cNames(1) = "Сделки"
    End If

    For i = 1 To bCount
        wsPart.Cells(3, i + 3).Value = b2cNames(i)
    Next i

    colTotal = bCount + 4
    colPrepay = bCount + 5
    colWait = bCount + 6
    colBrandSplit = bCount + 7

    wsPart.Cells(3, colTotal).Value = "Тотал сделок"
    wsPart.Cells(3, colPrepay).Value = "Кол-во предоплат"
    wsPart.Cells(3, colWait).Value = "Предоплаты без сделки"
    wsPart.Cells(3, colBrandSplit).Value = "Сплит по брендам"

    wsPart.Range(wsPart.Cells(3, 1), wsPart.Cells(3, colBrandSplit)).Font.Bold = True
    wsPart.Range(wsPart.Cells(3, 1), wsPart.Cells(3, colBrandSplit)).Interior.Color = RGB(54, 96, 146)
    wsPart.Range(wsPart.Cells(3, 1), wsPart.Cells(3, colBrandSplit)).Font.Color = RGB(255, 255, 255)

    cCount = dictSales.Count
    If cCount > 0 Then
        ReDim arrCompSorted(1 To cCount)
        ReDim arrSalesSorted(1 To cCount)
        idxLocal = 1
        For Each k In dictSales.Keys
            arrCompSorted(idxLocal) = CStr(k)
            arrSalesSorted(idxLocal) = dictSales(k)
            idxLocal = idxLocal + 1
        Next k

        For iSort = 1 To cCount - 1
            For jSort = iSort + 1 To cCount
                If arrSalesSorted(iSort) < arrSalesSorted(jSort) Then
                    tempN = arrSalesSorted(iSort)
                    arrSalesSorted(iSort) = arrSalesSorted(jSort)
                    arrSalesSorted(jSort) = tempN

                    tempS = arrCompSorted(iSort)
                    arrCompSorted(iSort) = arrCompSorted(jSort)
                    arrCompSorted(jSort) = tempS
                End If
            Next jSort
        Next iSort
    End If

    r = 4
    If cCount > 0 Then
        For iSort = 1 To cCount
            compU2 = arrCompSorted(iSort)
            compDisplay = compU2
            If dictBitrixOrigName.Exists(compU2) Then
                compDisplay = dictBitrixOrigName(compU2)
            End If

            wsPart.Cells(r, 1).Value = compDisplay
            kName = "Без КАМа"
            If dictBitrix_to_KAM.Exists(compU2) Then
                kName = dictBitrix_to_KAM(compU2)
            End If
            wsPart.Cells(r, 2).Value = kName

            wsPart.Cells(r, 3).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Лид"", SYS_DB_PARTNERS!$C:$C, $A" & r & "), SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Лид"", SYS_DB_PARTNERS!$C:$C, $A" & r & ", SYS_DB_PARTNERS!$B:$B, $C$1))"

            For i = 1 To bCount
                colLetter = Split(wsPart.Cells(3, i + 3).Address(True, False), "$")(0)
                wsPart.Cells(r, i + 3).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Сделка"", SYS_DB_PARTNERS!$C:$C, $A" & r & ", SYS_DB_PARTNERS!$D:$D, " & colLetter & "$3), SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Сделка"", SYS_DB_PARTNERS!$C:$C, $A" & r & ", SYS_DB_PARTNERS!$D:$D, " & colLetter & "$3, SYS_DB_PARTNERS!$B:$B, $C$1))"
            Next i

            colLetter = Split(wsPart.Cells(3, colTotal).Address(True, False), "$")(0)
            wsPart.Cells(r, colTotal).Formula = "=SUM(" & Split(wsPart.Cells(3, 4).Address(True, False), "$")(0) & r & ":" & Split(wsPart.Cells(3, bCount + 3).Address(True, False), "$")(0) & r & ")"

            wsPart.Cells(r, colPrepay).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Предоплата"", SYS_DB_PARTNERS!$C:$C, $A" & r & "), SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Предоплата"", SYS_DB_PARTNERS!$C:$C, $A" & r & ", SYS_DB_PARTNERS!$B:$B, $C$1))"

            wsPart.Cells(r, colWait).Formula = "=SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Без сделки"", SYS_DB_PARTNERS!$C:$C, $A" & r & ")"

            wsPart.Cells(r, colBrandSplit).Formula = "=GetPartnerBrandSplit($A" & r & ", $C$1)"

            r = r + 1
        Next iSort
    Else
        wsPart.Cells(r, 1).Value = "Нет сделок"
        r = r + 1
    End If

    wsPart.Cells(r, 1).Value = "ИТОГО"
    wsPart.Cells(r, 3).Formula = "=SUM(C4:C" & (r - 1) & ")"

    If cCount > 0 Then
        For i = 1 To bCount
            colLetter = Split(wsPart.Cells(3, i + 3).Address(True, False), "$")(0)
            wsPart.Cells(r, i + 3).Formula = "=SUM(" & colLetter & "4:" & colLetter & (r - 1) & ")"
        Next i
    End If

    colLetter = Split(wsPart.Cells(3, colTotal).Address(True, False), "$")(0)
    wsPart.Cells(r, colTotal).Formula = "=SUM(" & colLetter & "4:" & colLetter & (r - 1) & ")"

    colLetter = Split(wsPart.Cells(3, colPrepay).Address(True, False), "$")(0)
    wsPart.Cells(r, colPrepay).Formula = "=SUM(" & colLetter & "4:" & colLetter & (r - 1) & ")"

    colLetter = Split(wsPart.Cells(3, colWait).Address(True, False), "$")(0)
    wsPart.Cells(r, colWait).Formula = "=SUM(" & colLetter & "4:" & colLetter & (r - 1) & ")"

    wsPart.Range(wsPart.Cells(r, 1), wsPart.Cells(r, colBrandSplit)).Font.Bold = True
    wsPart.Range(wsPart.Cells(r, 1), wsPart.Cells(r, colBrandSplit)).Interior.Color = RGB(146, 208, 80)
    wsPart.Range(wsPart.Cells(3, 1), wsPart.Cells(r, colBrandSplit)).Borders.LineStyle = xlContinuous

    ' --- SECOND TABLE: Partners without deals (BI names) ---
    r2 = r + 3
    wsPart.Cells(r2, 1).Value = "Партнеры без сделок (имена из BI)"
    wsPart.Cells(r2, 1).Font.Bold = True
    wsPart.Cells(r2, 1).Font.Size = 12

    r2 = r2 + 1
    wsPart.Cells(r2, 1).Value = "Компания (название BI)"
    wsPart.Cells(r2, 2).Value = "КАМ"
    wsPart.Cells(r2, 3).Value = "Передачи лидов"

    wsPart.Range(wsPart.Cells(r2, 1), wsPart.Cells(r2, 3)).Font.Bold = True
    wsPart.Range(wsPart.Cells(r2, 1), wsPart.Cells(r2, 3)).Interior.Color = RGB(128, 128, 128)
    wsPart.Range(wsPart.Cells(r2, 1), wsPart.Cells(r2, 3)).Font.Color = RGB(255, 255, 255)

    Set dictBI_AllTimeLeads = CreateObject("Scripting.Dictionary")

    On Error Resume Next
    Set wsLeads = ActiveWorkbook.Sheets("лиды")
    On Error GoTo 0

    If Not wsLeads Is Nothing Then
        colLClient = 0
        colLPartner = 0
        colLDate = 0

        For c = 1 To wsLeads.Cells(1, wsLeads.Columns.Count).End(xlToLeft).Column
            hName = UCase(Trim(wsLeads.Cells(1, c).Value))
            If hName = "CLIENT_ID" Then colLClient = c
            If hName = "PARTNER" Then colLPartner = c
            If hName = "DATE" Then colLDate = c
        Next c

        If colLClient > 0 And colLPartner > 0 And colLDate > 0 Then
            lLr = wsLeads.Cells(wsLeads.Rows.Count, colLClient).End(xlUp).Row
            For i = 2 To lLr
                lPartRaw = Trim(CStr(wsLeads.Cells(i, colLPartner).Value))
                If lPartRaw <> "" Then
                    lPartU = UCase(lPartRaw)
                    dictBI_AllTimeLeads(lPartU) = dictBI_AllTimeLeads(lPartU) + 1
                End If
            Next i
        End If
    End If

    noSCount = 0
    For Each k In dictAllBI.Keys
        biNameStr = CStr(k)
        biNameU = UCase(biNameStr)
        bitrixRef = ""

        If dictBI_to_Bitrix.Exists(biNameU) Then
            bitrixRef = dictBI_to_Bitrix(biNameU)
        End If

        addToTable2 = False
        If bitrixRef = "" Then
            addToTable2 = True
        ElseIf Not dictSales.Exists(bitrixRef) Then
            addToTable2 = True
        ElseIf dictSales(bitrixRef) = 0 Then
            addToTable2 = True
        End If

        If addToTable2 Then
            noSCount = noSCount + 1
            ReDim Preserve arrNoSComp(1 To noSCount)
            ReDim Preserve arrNoSLeads(1 To noSCount)
            arrNoSComp(noSCount) = biNameStr
            If dictBI_AllTimeLeads.Exists(biNameU) Then
                arrNoSLeads(noSCount) = dictBI_AllTimeLeads(biNameU)
            Else
                arrNoSLeads(noSCount) = 0
            End If
        End If
    Next k

    startR2 = r2 + 1
    If noSCount > 0 Then
        For iSort = 1 To noSCount - 1
            For jSort = iSort + 1 To noSCount
                If arrNoSLeads(iSort) < arrNoSLeads(jSort) Then
                    tempN = arrNoSLeads(iSort)
                    arrNoSLeads(iSort) = arrNoSLeads(jSort)
                    arrNoSLeads(jSort) = tempN

                    tempS = arrNoSComp(iSort)
                    arrNoSComp(iSort) = arrNoSComp(jSort)
                    arrNoSComp(jSort) = tempS
                End If
            Next jSort
        Next iSort

        r2 = r2 + 1
        For iSort = 1 To noSCount
            cNoBI = arrNoSComp(iSort)
            wsPart.Cells(r2, 1).Value = cNoBI

            kName = "Без КАМа"
            If dictBI_to_KAM.Exists(cNoBI) Then
                kName = dictBI_to_KAM(cNoBI)
            End If

            wsPart.Cells(r2, 2).Value = kName
            wsPart.Cells(r2, 3).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Лид"", SYS_DB_PARTNERS!$F:$F, $A" & r2 & "), SUMIFS(SYS_DB_PARTNERS!$E:$E, SYS_DB_PARTNERS!$A:$A, ""Лид"", SYS_DB_PARTNERS!$F:$F, $A" & r2 & ", SYS_DB_PARTNERS!$B:$B, $C$1))"
            r2 = r2 + 1
        Next iSort
    Else
        r2 = r2 + 1
        wsPart.Cells(r2, 1).Value = "Все партнеры имеют сделки"
        r2 = r2 + 1
    End If

    wsPart.Cells(r2, 1).Value = "ИТОГО"
    wsPart.Cells(r2, 3).Formula = "=SUM(C" & startR2 & ":C" & (r2 - 1) & ")"

    wsPart.Range(wsPart.Cells(r2, 1), wsPart.Cells(r2, 3)).Font.Bold = True
    wsPart.Range(wsPart.Cells(r2, 1), wsPart.Cells(r2, 3)).Interior.Color = RGB(146, 208, 80)
    wsPart.Range(wsPart.Cells(startR2 - 1, 1), wsPart.Cells(r2, 3)).Borders.LineStyle = xlContinuous
    wsPart.Columns.AutoFit
End Sub

Public Sub CoreReportLogic(wsSrc As Worksheet)
    ' ==========================================
    ' UNIFIED BLOCK OF ALL VARIABLE DECLARATIONS
    ' ==========================================
    Dim wsRes As Worksheet, wsDyn As Worksheet, wsDynM As Worksheet
    Dim wsSys As Worksheet, wsMgr As Worksheet, wsSysPart As Worksheet
    Dim shtName As Variant
    Dim lastRow As Long, i As Long, c As Long, lastCol As Long
    Dim dbIdx As Long, pIdx As Long
    Dim carModel As String, dealType As String, stage As String
    Dim clientId As String, mgrName As String, seniorName As String
    Dim partnerStr As String, currentBrand As String, txtValue As String
    Dim dateStr As String, prepayDateStr As String
    Dim mKey As String, pKey As String, headerText As String
    Dim price As Double, commission As Double, revenue As Double  ' NEW: revenue variable
    Dim isCar As Boolean, isRealizedCar As Boolean
    Dim isPrepayment As Boolean, isWaitingCar As Boolean
    Dim dealDate As Date, prepayDate As Date, tempPrepayDate As Date
    Dim maxDate As Date, minDate As Date, todayDate As Date
    Dim startOfLastWeek As Date, endOfLastWeek As Date
    Dim colTovar As Long, colPrice As Long, colComm As Long
    Dim colB2C As Long, colDate As Long, colStage As Long
    Dim colClient As Long, colPrepayDate As Long, colManager As Long
    Dim colSenior As Long, colPartner As Long, colVin As Long  ' NEW: VIN column

    Dim dictClientBrand As Object, dictBrands As Object, dictB2C As Object
    Dim dictWaiting As Object, dictAllMonths As Object
    Dim dictWeekSales As Object, dictWeekComm As Object
    Dim dictWeekPrice As Object, dictWeekPrepay As Object
    Dim dictHistSales As Object, dictHistComm As Object
    Dim dictHistPrice As Object, dictHistPrepay As Object
    Dim dictMgrSalesAll As Object, dictAllMgrs As Object, dictMgrSenior As Object
    Dim dictPrepay As Object, dictClientStage As Object, dictSeniors As Object, gMgrs As Object

    Dim bCount As Long, b2cCount As Long, gCount As Long
    Dim brandNames() As String, b2cNames() As String
    Dim arrM() As String, arrMS() As Long

    Dim iTemp As Long, bIdx As Long, mIdxLocal As Long, iSortL As Long, jSortL As Long
    Dim tempNumLocal As Long, tempStrLocal As String
    Dim mk As Variant, k As Variant
    Dim sen As String, clientGlobalStage As String, maxMKeyString As String
    Dim d As Long, rIdx As Long, b2cR As Long, wSt As Long, wR As Long, kR As Long
    Dim bottomRow As Long, dmRow As Long, wRow As Long, totalWeeks As Long
    Dim hr1 As Long, hr2 As Long, wIdx As Integer
    Dim cLet As String, pLet As String, lastColL As String
    Dim wB2cRow As Long, b2cListRow As Long, colIdxL As Long, dRow As Long
    Dim mLabel As Integer, pLabel As Integer
    Dim tWS As Double, tWP As Double, tWC As Double, tWPrep As Double, hSales As Double
    Dim aBr As String, curBr As String, bN As String, aB2C As String
    Dim b2cStart As Long, cRow As Long, shareRow As Long, pStart As Long, prRow As Long
    Dim rrStart As Long, cCol As Long, rRow As Long
    Dim bNameCell As String, b2cNameCell As String
    Dim mRow As Long, startT As Long, idx2 As Long

    Dim chartDyn1 As ChartObject, chartDyn2 As ChartObject
    Dim cO1 As ChartObject, cO2 As ChartObject
    Dim kLabs As Variant, wMet As Variant, labelsMetrics As Variant, labelsPeriods As Variant
    Dim arrDB() As Variant, arrP() As Variant
    Dim monthList() As String, lastMRowLocal As Long

    Dim chartGroup As String, cleanDealType As String
    Dim vinValue As String  ' NEW: VIN holder

    ' ==========================================
    ' DICTIONARY INITIALIZATION
    ' ==========================================
    Set dictClientBrand = CreateObject("Scripting.Dictionary")
    Set dictBrands = CreateObject("Scripting.Dictionary")
    Set dictB2C = CreateObject("Scripting.Dictionary")
    Set dictWaiting = CreateObject("Scripting.Dictionary")
    Set dictAllMonths = CreateObject("Scripting.Dictionary")
    Set dictWeekSales = CreateObject("Scripting.Dictionary")
    Set dictWeekComm = CreateObject("Scripting.Dictionary")
    Set dictWeekPrice = CreateObject("Scripting.Dictionary")
    Set dictWeekPrepay = CreateObject("Scripting.Dictionary")
    Set dictHistSales = CreateObject("Scripting.Dictionary")
    Set dictHistComm = CreateObject("Scripting.Dictionary")
    Set dictHistPrice = CreateObject("Scripting.Dictionary")
    Set dictHistPrepay = CreateObject("Scripting.Dictionary")
    Set dictMgrSalesAll = CreateObject("Scripting.Dictionary")
    Set dictAllMgrs = CreateObject("Scripting.Dictionary")
    Set dictMgrSenior = CreateObject("Scripting.Dictionary")
    Set dictPrepay = CreateObject("Scripting.Dictionary")
    Set dictClientStage = CreateObject("Scripting.Dictionary")

    todayDate = Date
    startOfLastWeek = (todayDate - Weekday(todayDate, vbMonday)) - 6
    endOfLastWeek = startOfLastWeek + 6
    maxDate = DateSerial(2000, 1, 1)
    minDate = DateSerial(2050, 1, 1)

    colSenior = 0: colPartner = 0: colVin = 0  ' NEW: VIN column init
    lastCol = wsSrc.Cells(1, wsSrc.Columns.Count).End(xlToLeft).Column

    For c = 1 To lastCol
        headerText = Trim(UCase(CStr(wsSrc.Cells(1, c).Value)))
        Select Case headerText
            Case "ТОВАР": colTovar = c
            Case "ЦЕНА": colPrice = c
            Case "КОМИССИЯ СДЕЛКИ, РУБ", "КОМИССИЯ СДЕЛКИ РУБ", "КОМИССИЯ": colComm = c
            Case "ТИП СДЕЛКИ.B2C", "ТИП СДЕЛКИ B2C", "ТИП СДЕЛКИ. B2C", "ТИП СДЕЛКИ": colB2C = c
            Case "ПРЕДПОЛАГАЕМАЯ ДАТА ЗАКРЫТИЯ", "ДАТА ЗАКРЫТИЯ", "ДАТА": colDate = c
            Case "СТАДИЯ СДЕЛКИ": colStage = c
            Case "CLIENT_ID": colClient = c
            Case "ДАТА ПОЛУЧЕНИЯ АВАНСА", "ДАТА ВНЕСЕНИЯ ПРЕДОПЛАТЫ.РОЗНИЦА": colPrepayDate = c
            Case "МЕНЕДЖЕР СДЕЛКИ", "МЕНЕДЖЕР": colManager = c
            Case "ОТВЕТСТВЕННЫЙ ЗА СДЕЛКУ (СТАРШИЙ)": colSenior = c
            Case "КОМПАНИЯ": colPartner = c
            Case "VIN", "VIN НОМЕР": colVin = c  ' NEW: VIN column detection
        End Select
    Next c

    If colTovar = 0 Or colPrice = 0 Or colDate = 0 Or colStage = 0 Or colClient = 0 Or colManager = 0 Then
        Err.Raise vbObjectError + 513, "Сборка базы", "Базовые столбцы (Товар, Цена, Дата, Стадия и т.д.) не найдены на листе '" & wsSrc.Name & "'! Проверьте загрузку данных."
        Exit Sub
    End If

    lastRow = wsSrc.Cells(wsSrc.Rows.Count, colTovar).End(xlUp).Row

    ' CLIENT DOSSIER
    For i = 2 To lastRow
        clientId = CleanID(wsSrc.Cells(i, colClient).Value)
        If clientId <> "" Then
            txtValue = UCase(Trim(CStr(wsSrc.Cells(i, colTovar).Value)))
            If InStr(1, txtValue, "ВНЕСЕНИЕ АВАНСА") > 0 Then dictPrepay(clientId) = True

            stage = UCase(Trim(CStr(wsSrc.Cells(i, colStage).Value)))
            If stage <> "" Then
                If Not dictClientStage.Exists(clientId) Then dictClientStage(clientId) = stage
            End If
        End If
    Next i

    Application.DisplayAlerts = False
    For Each shtName In Array("Диаграмма", "Динамика", "Динамика месяцы", "Менеджеры", "SYS_DB", "SYS_DB_PARTNERS", "Воронка КАМ")
        On Error Resume Next
        ActiveWorkbook.Sheets(shtName).Delete
        On Error GoTo 0
    Next shtName
    Application.DisplayAlerts = True

    Set wsRes = Sheets.Add(After:=wsSrc)
    wsRes.Name = "Диаграмма"
    Set wsDyn = Sheets.Add(After:=wsRes)
    wsDyn.Name = "Динамика"
    Set wsDynM = Sheets.Add(After:=wsDyn)
    wsDynM.Name = "Динамика месяцы"
    Set wsMgr = Sheets.Add(After:=wsDynM)
    wsMgr.Name = "Менеджеры"
    Set wsSys = Sheets.Add(After:=wsMgr)
    wsSys.Name = "SYS_DB"
    Set wsSysPart = Sheets.Add(After:=wsSys)
    wsSysPart.Name = "SYS_DB_PARTNERS"

    ' ====================================================================
    ' EXPANDED SYS_DB HEADER: 18 columns (was 16)
    ' Col 13 = SeniorManager (was "N/A"), Col 14 = MinDate, Col 15 = MaxDate
    ' Col 16 = PrepayDate, Col 17 = Revenue (NEW), Col 18 = VIN (NEW)
    ' Col 19 = ChartGroup (was col 16)
    ' ====================================================================
    ' Re-indexed: col1=SaleMonth, col2=PrepayMonth, col3=Brand, col4=B2C,
    '   col5=SaleQty, col6=Price, col7=Comm, col8=PrepayQty, col9=WaitQty,
    '   col10=WaitMonth, col11=DealDate, col12=Manager,
    '   col13=SeniorManager, col14=MinDate, col15=MaxDate,
    '   col16=PrepayDate, col17=Revenue, col18=VIN, col19=ChartGroup
    wsSys.Range("A1:S1").Value = Array("SaleMonth", "PrepayMonth", "Brand", "B2C", "SaleQty", "Price", "Comm", "PrepayQty", "WaitQty", "WaitMonth", "DealDate", "Manager", "SeniorManager", "MinDate", "MaxDate", "PrepayDate", "Revenue", "VIN", "ChartGroup")
    wsSysPart.Range("A1:G1").Value = Array("Type", "Month", "Partner", "B2C", "Qty", "KAM", "Brand")

    ' EXPANDED arrDB to 19 columns (was 16)
    ReDim arrDB(1 To lastRow, 1 To 19)
    ReDim arrP(1 To lastRow * 3, 1 To 7)

    dbIdx = 0: pIdx = 0

    ' ============================================================
    ' MAIN LOOP OVER RAW DATA
    ' ============================================================
    For i = 2 To lastRow
        carModel = Trim(CStr(wsSrc.Cells(i, colTovar).Value))
        stage = Trim(UCase(CStr(wsSrc.Cells(i, colStage).Value)))
        clientId = CleanID(wsSrc.Cells(i, colClient).Value)
        mgrName = Trim(CStr(wsSrc.Cells(i, colManager).Value))
        If mgrName = "" Then mgrName = "Не указан"

        seniorName = "Без старшего"
        If colSenior > 0 Then
            seniorName = Trim(CStr(wsSrc.Cells(i, colSenior).Value))
            If seniorName = "" Then seniorName = "Без старшего"
        End If
        dictMgrSenior(mgrName) = seniorName

        price = 0
        txtValue = Replace(Replace(CStr(wsSrc.Cells(i, colPrice).Value), " ", ""), ",", ".")
        If txtValue <> "" And IsNumeric(txtValue) Then price = val(txtValue)

        commission = 0
        txtValue = Replace(Replace(CStr(wsSrc.Cells(i, colComm).Value), " ", ""), ",", ".")
        If txtValue <> "" And IsNumeric(txtValue) Then commission = val(txtValue)

        dealDate = ParseDateCustom(CStr(wsSrc.Cells(i, colDate).Value))
        prepayDate = dealDate

        If colPrepayDate > 0 Then
            prepayDateStr = Trim(CStr(wsSrc.Cells(i, colPrepayDate).Value))
            If prepayDateStr <> "" Then
                tempPrepayDate = ParseDateCustom(prepayDateStr)
                If tempPrepayDate <> DateSerial(1900, 1, 1) Then prepayDate = tempPrepayDate
            End If
        End If

        If Year(dealDate) > 1900 And Year(dealDate) < 2050 Then
            If dealDate > maxDate Then maxDate = dealDate
            If dealDate < minDate Then minDate = dealDate
        End If

        dealType = "(пусто)"
        If colB2C > 0 Then dealType = Trim(CStr(wsSrc.Cells(i, colB2C).Value))
        If dealType = "" Then dealType = "(пусто)"

        partnerStr = ""
        If colPartner > 0 Then partnerStr = Trim(CStr(wsSrc.Cells(i, colPartner).Value))

        ' NEW: Read VIN value
        vinValue = ""
        If colVin > 0 Then vinValue = Trim(CStr(wsSrc.Cells(i, colVin).Value))

        clientGlobalStage = stage
        If clientId <> "" And dictClientStage.Exists(clientId) Then clientGlobalStage = dictClientStage(clientId)

        currentBrand = "": isRealizedCar = False: isPrepayment = False: isWaitingCar = False

        If carModel <> "" And UCase(carModel) <> "ТОВАР" Then
            txtValue = UCase(carModel)
            If InStr(1, txtValue, "ВНЕСЕНИЕ АВАНСА") > 0 Then
                isPrepayment = True
                If clientId <> "" And dictClientBrand.Exists(clientId) Then
                    currentBrand = dictClientBrand(clientId)
                Else
                    currentBrand = "НЕИЗВЕСТНЫЙ БРЕНД"
                End If
            Else
                isCar = True
                If InStr(1, txtValue, "КРЕДИТ") > 0 Or InStr(1, txtValue, "КАСКО") > 0 Or InStr(1, txtValue, "ОСАГО") > 0 Or InStr(1, txtValue, "ГАП СБЕР") > 0 Or InStr(1, txtValue, "ФИНКАСКО") > 0 Then isCar = False

                If isCar Then
                    carModel = Replace(carModel, Chr(160), " ")
                    If InStr(carModel, " ") > 0 Then carModel = Left(carModel, InStr(carModel, " ") - 1)
                    currentBrand = UCase(Trim(carModel))
                    If InStr(1, currentBrand, "JETOUR") > 0 Then currentBrand = "JETOUR"
                    If InStr(1, currentBrand, "SOLARIS") > 0 Or InStr(1, currentBrand, "СОЛЯРИС") > 0 Then currentBrand = "SOLARIS"
                    If currentBrand = "X-CROSS" Then currentBrand = "LADA"
                    If currentBrand = "GEELY" Or currentBrand = "BELGEE" Or currentBrand = "БЕЛДЖИ" Or currentBrand = "KNEWSTAR" Then currentBrand = "G B K"
                    If currentBrand = "CHERY" Or currentBrand = "TENET" Or currentBrand = "ЧЕРИ" Then currentBrand = "TENET"

                    If InStr(1, stage, "ЗАКРЫТО И РЕАЛИЗОВАН") > 0 Or InStr(1, clientGlobalStage, "ЗАКРЫТО И РЕАЛИЗОВАН") > 0 Then
                        isRealizedCar = True
                    Else
                        If clientId <> "" And dictPrepay.Exists(clientId) Then
                            If InStr(1, clientGlobalStage, "ЗАКРЫТО") = 0 And InStr(1, clientGlobalStage, "ОТКАЗ") = 0 And InStr(1, clientGlobalStage, "ПРОИГРАН") = 0 And InStr(1, clientGlobalStage, "НЕ РЕАЛИЗОВАН") = 0 Then isWaitingCar = True
                        End If
                    End If
                End If
            End If

            If isWaitingCar And currentBrand <> "" Then dictWaiting(currentBrand) = dictWaiting(currentBrand) + 1

            If currentBrand <> "" Or isPrepayment Then
                mKey = Format(dealDate, "yyyy-mm"): pKey = Format(prepayDate, "yyyy-mm")
                If Year(dealDate) > 1900 Then dictAllMonths(mKey) = True
                If isPrepayment And Year(prepayDate) > 1900 Then dictAllMonths(pKey) = True

                dbIdx = dbIdx + 1

                cleanDealType = UCase(Replace(Trim(dealType), " ", ""))
                If cleanDealType = "МП1" Or cleanDealType = "МП2" Or cleanDealType = "МП3" Or cleanDealType = "ВХОДЯЩАЯЗАЯВКА" Then
                    chartGroup = "Partners"
                Else
                    chartGroup = "Новые авто"
                End If

                ' ============================================================
                ' REVENUE CALCULATION (NEW)
                ' Logic: commission / 1.22 ONLY when stage = "ЗАКРЫТО И РЕАЛИЗОВАН"
                ' AND "Goods" column does NOT contain exclusion markers:
                '   ВНЕСЕНИЕ АВАНСА, КРЕДИТ, КАСКО, ОСАГО, ГАП СБЕР, ФИНКАСКО
                ' ============================================================
                revenue = 0
                If isRealizedCar Then
                    txtValue = UCase(carModel)
                    If InStr(1, txtValue, "ВНЕСЕНИЕ АВАНСА") = 0 And _
                       InStr(1, txtValue, "КРЕДИТ") = 0 And _
                       InStr(1, txtValue, "КАСКО") = 0 And _
                       InStr(1, txtValue, "ОСАГО") = 0 And _
                       InStr(1, txtValue, "ГАП СБЕР") = 0 And _
                       InStr(1, txtValue, "ФИНКАСКО") = 0 Then
                        revenue = Round(commission / 1.22, 2)  ' VAT 20% deduction
                    End If
                End If

                If isRealizedCar Then
                    arrDB(dbIdx, 1) = "'" & mKey: arrDB(dbIdx, 5) = 1
                    arrDB(dbIdx, 6) = price: arrDB(dbIdx, 7) = commission
                    arrDB(dbIdx, 17) = revenue   ' NEW: Revenue (KvNew) col 17
                    If partnerStr <> "" Then
                        pIdx = pIdx + 1: arrP(pIdx, 1) = "Сделка"
                        arrP(pIdx, 2) = "'" & mKey: arrP(pIdx, 3) = partnerStr
                        arrP(pIdx, 4) = dealType: arrP(pIdx, 5) = 1: arrP(pIdx, 7) = currentBrand
                    End If
                End If

                If isPrepayment Then
                    arrDB(dbIdx, 2) = "'" & pKey: arrDB(dbIdx, 8) = 1
                    If partnerStr <> "" Then
                        pIdx = pIdx + 1: arrP(pIdx, 1) = "Предоплата"
                        arrP(pIdx, 2) = "'" & pKey: arrP(pIdx, 3) = partnerStr: arrP(pIdx, 5) = 1: arrP(pIdx, 7) = currentBrand
                    End If
                End If

                If isWaitingCar Then
                    arrDB(dbIdx, 9) = 1: arrDB(dbIdx, 10) = "'" & pKey
                    If partnerStr <> "" Then
                        pIdx = pIdx + 1: arrP(pIdx, 1) = "Без сделки"
                        arrP(pIdx, 2) = "'" & pKey: arrP(pIdx, 3) = partnerStr: arrP(pIdx, 5) = 1: arrP(pIdx, 7) = currentBrand
                    End If
                End If

                arrDB(dbIdx, 3) = currentBrand: arrDB(dbIdx, 4) = dealType
                arrDB(dbIdx, 11) = CLng(dealDate): arrDB(dbIdx, 12) = mgrName
                arrDB(dbIdx, 13) = seniorName    ' NEW: SeniorManager col 13
                arrDB(dbIdx, 16) = CLng(prepayDate)
                arrDB(dbIdx, 18) = vinValue      ' NEW: VIN col 18
                arrDB(dbIdx, 19) = chartGroup    ' ChartGroup moved to col 19

                If isRealizedCar Then
                    dictBrands(currentBrand) = dictBrands(currentBrand) + 1
                    dictB2C(dealType) = dictB2C(dealType) + 1
                    dictAllMgrs(mgrName) = True
                    If dealDate >= startOfLastWeek And dealDate <= endOfLastWeek Then
                        dictWeekSales(currentBrand) = dictWeekSales(currentBrand) + 1
                        dictWeekPrice(currentBrand) = dictWeekPrice(currentBrand) + price
                        dictWeekComm(currentBrand) = dictWeekComm(currentBrand) + commission
                    End If
                    dictHistSales(currentBrand & "|" & mKey) = dictHistSales(currentBrand & "|" & mKey) + 1
                    dictHistPrice(currentBrand & "|" & mKey) = dictHistPrice(currentBrand & "|" & mKey) + price
                    dictHistComm(currentBrand & "|" & mKey) = dictHistComm(currentBrand & "|" & mKey) + commission
                    dictMgrSalesAll(mgrName) = dictMgrSalesAll(mgrName) + 1
                End If

                If isPrepayment Then
                    If prepayDate >= startOfLastWeek And prepayDate <= endOfLastWeek Then dictWeekPrepay(currentBrand) = dictWeekPrepay(currentBrand) + 1
                    dictHistPrepay(currentBrand & "|" & pKey) = dictHistPrepay(currentBrand & "|" & pKey) + 1
                    dictAllMgrs(mgrName) = True
                End If
            End If
        End If
    Next i

    If maxDate < DateSerial(2020, 1, 1) Then maxDate = Date
    If minDate > DateSerial(2040, 1, 1) Then minDate = maxDate
    maxMKeyString = Format(maxDate, "yyyy-mm")

    ' Write the huge data array (EXPANDED to 19 columns)
    If dbIdx > 0 Then wsSys.Range("A2").Resize(dbIdx, 19).Value = arrDB
    If pIdx > 0 Then wsSysPart.Range("A2").Resize(pIdx, 7).Value = arrP
    wsSys.Visible = xlSheetVeryHidden: wsSysPart.Visible = xlSheetVeryHidden

    ' Write system dates (so the array does not overwrite them!)
    wsSys.Cells(1, 14).Value = CLng(minDate): wsSys.Cells(2, 14).Value = CLng(maxDate)

    Call BuildBrandSplitsCache

    mCount = dictAllMonths.Count
    If mCount > 0 Then
        ReDim monthList(0 To mCount - 1)
        mIdxLocal = 0
        For Each mk In dictAllMonths.Keys
            monthList(mIdxLocal) = CStr(mk): mIdxLocal = mIdxLocal + 1
        Next mk
        For iSortL = 0 To mCount - 2
            For jSortL = iSortL + 1 To mCount - 1
                If monthList(iSortL) > monthList(jSortL) Then
                    tempStrLocal = monthList(iSortL): monthList(iSortL) = monthList(jSortL): monthList(jSortL) = tempStrLocal
                End If
            Next jSortL
        Next iSortL
    End If

    wsSys.Cells(1, 13).Value = "Весь период"
    lastMRowLocal = 1
    If mCount > 0 Then
        For mIdxLocal = 0 To UBound(monthList)
            wsSys.Cells(mIdxLocal + 2, 13).Value = "'" & monthList(mIdxLocal)
        Next mIdxLocal
        lastMRowLocal = UBound(monthList) + 2
    End If

    bCount = dictBrands.Count
    If bCount > 0 Then
        ReDim brandNames(1 To bCount)
        iTemp = 1
        For Each mk In dictBrands.Keys
            brandNames(iTemp) = CStr(mk)
            iTemp = iTemp + 1
        Next mk
    End If

    b2cCount = dictB2C.Count
    If b2cCount > 0 Then
        ReDim b2cNames(1 To b2cCount)
        iTemp = 1
        For Each mk In dictB2C.Keys
            b2cNames(iTemp) = CStr(mk)
            iTemp = iTemp + 1
        Next mk
    End If

    ' =========================================================================
    ' === DIAGRAM SHEET (PRESENTATION SLIDE + 2 CHARTS) ===
    ' =========================================================================
    wsRes.Activate
    ActiveWindow.DisplayGridlines = False
    wsRes.Cells.Interior.Color = RGB(243, 244, 246)

    wsRes.Range("A1:C1").Interior.Color = RGB(255, 255, 255)
    wsRes.Range("A1:C1").Borders.LineStyle = xlContinuous
    wsRes.Cells(1, 1).Value = "ФИЛЬТР ДАННЫХ ->"
    wsRes.Cells(1, 1).Font.Bold = True
    With wsRes.Cells(1, 3)
        .NumberFormat = "@"
        .Value = maxMKeyString
        .Interior.Color = RGB(255, 255, 204)
        .Font.Bold = True
        If mCount > 0 Then
            .Validation.Delete
            .Validation.Add Type:=xlValidateList, Formula1:="=SYS_DB!$M$1:$M$" & lastMRowLocal
        End If
    End With

    wsRes.Range("E2:H7").Interior.Color = RGB(255, 255, 255)
    wsRes.Range("E2").Value = "СРАВНЕНИЕ ПЕРИОДОВ (MoM):"
    wsRes.Range("E2:H2").Merge
    wsRes.Range("E2").Font.Bold = True
    wsRes.Range("E2").Interior.Color = RGB(54, 96, 146)
    wsRes.Range("E2").Font.Color = RGB(255, 255, 255)

    wsRes.Range("E3").Value = "Дата С:"
    wsRes.Range("F3").Value = DateSerial(Year(Date), Month(Date), 1)
    wsRes.Range("E4").Value = "Дата ПО:"
    wsRes.Range("F4").Value = Date
    wsRes.Range("F3:F4").Interior.Color = RGB(255, 255, 204)
    wsRes.Range("F3:F4").Borders.LineStyle = xlContinuous
    wsRes.Range("F3:H4").NumberFormat = "dd.mm.yyyy"

    wsRes.Range("G3").Formula = "=EDATE(F3, -1)"
    wsRes.Range("G4").Formula = "=EDATE(F4, -1)"
    wsRes.Range("G3:G4").Font.Color = RGB(128, 128, 128)

    wsRes.Range("E5").Value = "Метрика"
    wsRes.Range("F5").Value = "Выбрано"
    wsRes.Range("G5").Value = "Прошл. мес"
    wsRes.Range("H5").Value = "Динамика"
    wsRes.Range("E5:H5").Font.Bold = True
    wsRes.Range("E5:H5").Borders(xlEdgeBottom).LineStyle = xlContinuous

    wsRes.Range("E6").Value = "Сделки (шт)"
    wsRes.Range("E7").Value = "Авансы (шт)"
    wsRes.Range("F6").Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&F3, SYS_DB!$K:$K, ""<=""&F4)"
    wsRes.Range("G6").Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&G3, SYS_DB!$K:$K, ""<=""&G4)"
    wsRes.Range("H6").Formula = "=IF(G6=0, 1, (F6/G6)-1)"
    wsRes.Range("F7").Formula = "=SUMIFS(SYS_DB!$H:$H, SYS_DB!$P:$P, "">=""&F3, SYS_DB!$P:$P, ""<=""&F4)"
    wsRes.Range("G7").Formula = "=SUMIFS(SYS_DB!$H:$H, SYS_DB!$P:$P, "">=""&G3, SYS_DB!$P:$P, ""<=""&G4)"
    wsRes.Range("H7").Formula = "=IF(G7=0, 1, (F7/G7)-1)"
    wsRes.Range("H6:H7").NumberFormat = "0%"
    wsRes.Range("E2:H7").Borders.LineStyle = xlContinuous

    ' PREPARE DAYS FOR CHART 1 (PARTNERS) in N:Q
    wsRes.Range("N2:Q2").Value = Array("День", "Сделки", "Предоплаты", "Выходные")
    For d = 1 To 31
        wsRes.Range("N" & d + 2).Formula = "=IF($C$1=""Весь период"", " & _
        "IF(MONTH(DATE(YEAR(TODAY()), MONTH(TODAY()), " & d & "))<>MONTH(TODAY()), """", DATE(YEAR(TODAY()), MONTH(TODAY()), " & d & ")), " & _
        "IFERROR(IF(MONTH(DATE(VALUE(LEFT($C$1,4)), VALUE(RIGHT($C$1,2)), " & d & "))<>VALUE(RIGHT($C$1,2)), """", DATE(VALUE(LEFT($C$1,4)), VALUE(RIGHT($C$1,2)), " & d & ")), """"))"

        wsRes.Range("O" & d + 2).Formula = "=IF(N" & d + 2 & "="""","""", SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, N" & d + 2 & ", SYS_DB!$S:$S, ""Partners""))"
        wsRes.Range("P" & d + 2).Formula = "=IF(N" & d + 2 & "="""","""", SUMIFS(SYS_DB!$H:$H, SYS_DB!$P:$P, N" & d + 2 & ", SYS_DB!$S:$S, ""Partners""))"
        wsRes.Range("Q" & d + 2).Formula = "=IF(N" & d + 2 & "="""","""", IF(WEEKDAY(N" & d + 2 & ", 2)>5, MAX(O$3:P$33)*1.2, 0))"
    Next d
    wsRes.Range("N3:N33").NumberFormat = "dd.mm"

    ' PREPARE DAYS FOR CHART 2 (NEW CARS) in S:V
    wsRes.Range("S2:V2").Value = Array("День", "Сделки", "Предоплаты", "Выходные")
    For d = 1 To 31
        wsRes.Range("S" & d + 2).Formula = "=N" & d + 2
        wsRes.Range("T" & d + 2).Formula = "=IF(S" & d + 2 & "="""","""", SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, S" & d + 2 & ", SYS_DB!$S:$S, ""Новые авто""))"
        wsRes.Range("U" & d + 2).Formula = "=IF(S" & d + 2 & "="""","""", SUMIFS(SYS_DB!$H:$H, SYS_DB!$P:$P, S" & d + 2 & ", SYS_DB!$S:$S, ""Новые авто""))"
        wsRes.Range("V" & d + 2).Formula = "=IF(S" & d + 2 & "="""","""", IF(WEEKDAY(S" & d + 2 & ", 2)>5, MAX(T$3:U$33)*1.2, 0))"
    Next d
    wsRes.Range("S3:S33").NumberFormat = "dd.mm"

    wsRes.Cells(11, 1).Value = "Марка авто"
    wsRes.Cells(11, 2).Value = "Количество"
    rIdx = 12
    For Each mk In dictBrands.Keys
        wsRes.Cells(rIdx, 1).Value = CStr(mk)
        wsRes.Cells(rIdx, 2).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, $A" & rIdx & "), SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, $A" & rIdx & ", SYS_DB!$A:$A, $C$1))"
        rIdx = rIdx + 1
    Next mk
    wsRes.Cells(rIdx, 1).Value = "Общий итог"
    wsRes.Cells(rIdx, 2).Formula = "=IF($C$1=""Весь период"", SUM(SYS_DB!$E:$E), SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1))"
    If rIdx > 12 Then wsRes.Range("A12:B" & rIdx - 1).Sort Key1:=wsRes.Range("B12"), Order1:=xlDescending

    wsRes.Range("A11:B" & rIdx).Interior.Color = RGB(255, 255, 255)
    wsRes.Range("A11:B11").Interior.Color = RGB(64, 64, 64)
    wsRes.Range("A11:B11").Font.Color = RGB(255, 255, 255)
    wsRes.Range("A11:B" & rIdx).Borders.LineStyle = xlContinuous

    ' SMART BRAND CHART IN COLUMNS (X:Y)
    wsRes.Range("X11").Value = "Бренд (Топ)"
    wsRes.Range("Y11").Value = "Кол-во"
    For i = 1 To 7
        wsRes.Range("X" & 11 + i).Formula = "=IF(ISNUMBER(B" & 11 + i & "), IF(B" & 11 + i & ">0, A" & 11 + i & ", NA()), NA())"
        wsRes.Range("Y" & 11 + i).Formula = "=IF(ISNUMBER(B" & 11 + i & "), IF(B" & 11 + i & ">0, B" & 11 + i & ", NA()), NA())"
    Next i
    wsRes.Range("X19").Value = "Другие"
    If (rIdx - 1) >= 19 Then
        wsRes.Range("Y19").Formula = "=IF(SUM(B19:B" & (rIdx - 1) & ")>0, SUM(B19:B" & (rIdx - 1) & "), NA())"
    Else
        wsRes.Range("Y19").Formula = "=NA()"
    End If

    Set cO1 = wsRes.ChartObjects.Add(Left:=wsRes.Range("D11").Left, Top:=wsRes.Range("D11").Top, Width:=350, Height:=220)
    With cO1.Chart
        .SetSourceData Source:=wsRes.Range("X11:Y19")
        .PlotVisibleOnly = False
        .ChartType = xlPie
        .HasTitle = True
        .ChartTitle.Text = "Сплит по брендам"
        .ApplyDataLabels xlDataLabelsShowLabelAndPercent
        .ChartArea.Format.Fill.ForeColor.RGB = RGB(255, 255, 255)
        .ChartArea.Format.Line.Visible = msoFalse
    End With

    b2cStart = rIdx + 2
    wsRes.Cells(b2cStart, 1).Value = "Тип сделки.B2C"
    wsRes.Cells(b2cStart, 2).Value = "Количество"
    b2cR = b2cStart + 1
    For Each mk In dictB2C.Keys
        wsRes.Cells(b2cR, 1).Value = CStr(mk)
        wsRes.Cells(b2cR, 2).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB!$E:$E, SYS_DB!$D:$D, $A" & b2cR & "), SUMIFS(SYS_DB!$E:$E, SYS_DB!$D:$D, $A" & b2cR & ", SYS_DB!$A:$A, $C$1))"
        b2cR = b2cR + 1
    Next mk

    If b2cR > b2cStart + 1 Then wsRes.Range("A" & b2cStart + 1 & ":B" & b2cR - 1).Sort Key1:=wsRes.Range("B" & b2cStart + 1), Order1:=xlDescending
    wsRes.Range("A" & b2cStart & ":B" & b2cR - 1).Interior.Color = RGB(255, 255, 255)
    wsRes.Range("A" & b2cStart & ":B" & b2cStart).Interior.Color = RGB(64, 64, 64)
    wsRes.Range("A" & b2cStart & ":B" & b2cStart).Font.Color = RGB(255, 255, 255)
    wsRes.Range("A" & b2cStart & ":B" & b2cR - 1).Borders.LineStyle = xlContinuous

    If b2cR > b2cStart + 1 Then
        Set cO2 = wsRes.ChartObjects.Add(Left:=wsRes.Range("D" & b2cStart).Left, Top:=wsRes.Range("D" & b2cStart).Top, Width:=350, Height:=220)
        With cO2.Chart
            .SetSourceData Source:=wsRes.Range("A" & b2cStart + 1 & ":B" & b2cR - 1)
            .PlotVisibleOnly = False
            .ChartType = xlPie
            .HasTitle = True
            .ChartTitle.Text = "Тип сделки.B2C"
            .ApplyDataLabels xlDataLabelsShowLabelAndPercent
            .ChartArea.Format.Fill.ForeColor.RGB = RGB(255, 255, 255)
            .ChartArea.Format.Line.Visible = msoFalse
        End With
    End If

    ' BIG CHART 1 (PARTNERS)
    Set chartDyn1 = wsRes.ChartObjects.Add(Left:=wsRes.Range("J2").Left, Top:=wsRes.Range("J2").Top, Width:=650, Height:=300)
    With chartDyn1.Chart
        .SetSourceData Source:=wsRes.Range("N2:Q33"), PlotBy:=xlColumns
        .PlotVisibleOnly = False
        .ChartType = xlLineMarkers
        .HasTitle = True
        .ChartTitle.Text = "Динамика: Partners (МП и Входящие)"

        .FullSeriesCollection(3).ChartType = xlColumnClustered
        .FullSeriesCollection(3).Format.Fill.ForeColor.RGB = RGB(230, 230, 230)
        .FullSeriesCollection(3).Format.Line.Visible = msoFalse
        .FullSeriesCollection(3).AxisGroup = 2
        .HasAxis(xlValue, xlSecondary) = False

        .FullSeriesCollection(1).HasDataLabels = True
        With .FullSeriesCollection(1).DataLabels
            .NumberFormat = "[=0]"""";0"
            .Position = xlLabelPositionAbove
            .Font.Bold = True
            .Font.Color = RGB(68, 114, 196)
        End With

        .FullSeriesCollection(2).HasDataLabels = True
        With .FullSeriesCollection(2).DataLabels
            .NumberFormat = "[=0]"""";0"
            .Position = xlLabelPositionBelow
            .Font.Bold = True
            .Font.Color = RGB(237, 125, 49)
        End With

        .FullSeriesCollection(3).HasDataLabels = False
        .ChartArea.Format.Fill.ForeColor.RGB = RGB(255, 255, 255)
        .ChartArea.Format.Line.Visible = msoFalse
        .Axes(xlCategory).TickLabels.NumberFormat = "dd.mm"
    End With

    ' BIG CHART 2 (NEW CARS)
    Set chartDyn2 = wsRes.ChartObjects.Add(Left:=wsRes.Range("J24").Left, Top:=wsRes.Range("J24").Top, Width:=650, Height:=300)
    With chartDyn2.Chart
        .SetSourceData Source:=wsRes.Range("S2:V33"), PlotBy:=xlColumns
        .PlotVisibleOnly = False
        .ChartType = xlLineMarkers
        .HasTitle = True
        .ChartTitle.Text = "Динамика: Новые Авто (Остальные B2C)"

        .FullSeriesCollection(3).ChartType = xlColumnClustered
        .FullSeriesCollection(3).Format.Fill.ForeColor.RGB = RGB(230, 230, 230)
        .FullSeriesCollection(3).Format.Line.Visible = msoFalse
        .FullSeriesCollection(3).AxisGroup = 2
        .HasAxis(xlValue, xlSecondary) = False

        .FullSeriesCollection(1).HasDataLabels = True
        With .FullSeriesCollection(1).DataLabels
            .NumberFormat = "[=0]"""";0"
            .Position = xlLabelPositionAbove
            .Font.Bold = True
            .Font.Color = RGB(68, 114, 196)
        End With

        .FullSeriesCollection(2).HasDataLabels = True
        With .FullSeriesCollection(2).DataLabels
            .NumberFormat = "[=0]"""";0"
            .Position = xlLabelPositionBelow
            .Font.Bold = True
            .Font.Color = RGB(237, 125, 49)
        End With

        .FullSeriesCollection(3).HasDataLabels = False
        .ChartArea.Format.Fill.ForeColor.RGB = RGB(255, 255, 255)
        .ChartArea.Format.Line.Visible = msoFalse
        .Axes(xlCategory).TickLabels.NumberFormat = "dd.mm"
    End With

    wSt = b2cR + 1
    wsRes.Cells(wSt, 1).Value = "Клиенты в ожидании"
    wsRes.Cells(wSt, 1).Font.Bold = True
    wsRes.Cells(wSt + 1, 1).Value = "Марка авто"
    wsRes.Cells(wSt + 1, 2).Value = "Кол-во"

    wR = wSt + 2
    For Each mk In dictWaiting.Keys
        wsRes.Cells(wR, 1).Value = CStr(mk)
        wsRes.Cells(wR, 2).Formula = "=SUMIFS(SYS_DB!$I:$I, SYS_DB!$C:$C, $A" & wR & ")"
        wR = wR + 1
    Next mk

    wsRes.Cells(wR, 1).Value = "Всего в ожидании"
    wsRes.Cells(wR, 2).Formula = "=SUM(SYS_DB!$I:$I)"
    wsRes.Range("A" & wR & ":B" & wR).Font.Bold = True

    wsRes.Range("A" & wSt & ":B" & wR).Interior.Color = RGB(255, 255, 255)
    wsRes.Range("A" & wSt + 1 & ":B" & wSt + 1).Interior.Color = RGB(192, 0, 0)
    wsRes.Range("A" & wSt + 1 & ":B" & wSt + 1).Font.Color = RGB(255, 255, 255)
    wsRes.Range("A" & wSt + 1 & ":B" & wR).Borders.LineStyle = xlContinuous

    kR = wR + 2
    kLabs = Array("ARPU тотал", "ARPU китай", "ARPU Лада", "Средний чек тотал", "Средний чек китай", "Средний чек лада")
    For iSortL = 0 To 5
        wsRes.Cells(kR + iSortL, 1).Value = kLabs(iSortL)
        wsRes.Cells(kR + iSortL, 1).Font.Bold = True
    Next iSortL

    ' Revenue KPI formulas — use Revenue column (Q = col 17) for clean ARPU
    wsRes.Cells(kR, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUM(SYS_DB!$Q:$Q)/SUM(SYS_DB!$E:$E), SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$A:$A, $C$1)/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1)), 0)"
    wsRes.Cells(kR + 1, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$C:$C, ""<>LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, ""<>LADA""), SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""<>LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""<>LADA"")), 0)"
    wsRes.Cells(kR + 2, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$C:$C, ""LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, ""LADA""), SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""LADA"")), 0)"
    wsRes.Cells(kR + 3, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUM(SYS_DB!$F:$F)/SUM(SYS_DB!$E:$E), SUMIFS(SYS_DB!$F:$F, SYS_DB!$A:$A, $C$1)/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1)), 0)"
    wsRes.Cells(kR + 4, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUMIFS(SYS_DB!$F:$F, SYS_DB!$C:$C, ""<>LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, ""<>LADA""), SUMIFS(SYS_DB!$F:$F, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""<>LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""<>LADA"")), 0)"
    wsRes.Cells(kR + 5, 2).Formula = "=IFERROR(IF($C$1=""Весь период"", SUMIFS(SYS_DB!$F:$F, SYS_DB!$C:$C, ""LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, ""LADA""), SUMIFS(SYS_DB!$F:$F, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""LADA"")/SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1, SYS_DB!$C:$C, ""LADA"")), 0)"

    wsRes.Range("A" & kR & ":B" & kR + 5).Interior.Color = RGB(255, 255, 255)
    wsRes.Range("A" & kR & ":B" & kR + 2).Borders.LineStyle = xlContinuous
    wsRes.Range("A" & kR + 3 & ":B" & kR + 5).Borders.LineStyle = xlContinuous
    wsRes.Range("B" & kR & ":B" & kR + 5).NumberFormat = "#,##0"

    bottomRow = kR + 7
    wsRes.Cells(bottomRow, 1).Value = "Сплит по брендам (текстом):"
    wsRes.Cells(bottomRow, 1).Font.Bold = True
    wsRes.Cells(bottomRow, 1).Interior.Color = RGB(64, 64, 64)
    wsRes.Cells(bottomRow, 1).Font.Color = RGB(255, 255, 255)
    wsRes.Range(wsRes.Cells(bottomRow, 1), wsRes.Cells(bottomRow, 8)).Merge

    wsRes.Cells(bottomRow + 1, 1).Formula = "=GetTotalBrandSplit($C$1)"
    wsRes.Range(wsRes.Cells(bottomRow + 1, 1), wsRes.Cells(bottomRow + 1, 8)).Merge
    wsRes.Cells(bottomRow + 1, 1).Font.Size = 12
    wsRes.Cells(bottomRow + 1, 1).Font.Bold = True
    wsRes.Cells(bottomRow + 1, 1).WrapText = True
    wsRes.Rows(bottomRow + 1).RowHeight = 40
    wsRes.Range(wsRes.Cells(bottomRow + 1, 1), wsRes.Cells(bottomRow + 1, 8)).Interior.Color = RGB(255, 255, 255)

    wsRes.Columns("A:B").ColumnWidth = 16
    wsRes.Columns("E:H").ColumnWidth = 13
    wsRes.Columns("N:AB").Hidden = True

    ' =========================================================================
    ' === DYNAMICS MONTHS SHEET ===
    ' =========================================================================
    wsDynM.Activate
    wsDynM.Cells(1, 1).Value = "ВЫБЕРИТЕ МЕСЯЦ ДЛЯ АНАЛИЗА НЕДЕЛЬ ->"
    wsDynM.Cells(1, 1).Font.Bold = True
    With wsDynM.Cells(1, 3)
        .NumberFormat = "@"
        .Value = maxMKeyString
        .Interior.Color = RGB(255, 255, 204)
        .Font.Bold = True
        .Borders.LineStyle = xlContinuous
        If mCount > 0 Then
            .Validation.Delete
            .Validation.Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Operator:=xlBetween, Formula1:="=SYS_DB!$M$1:$M$" & lastMRowLocal
        End If
    End With

    wsDynM.Cells(1, 4).Value = "После смены фильтра ->"
    wsDynM.Cells(1, 4).Font.Italic = True
    wsDynM.Cells(1, 4).HorizontalAlignment = xlRight

    wsDynM.Cells(1, 15).Formula = "=IF($C$1=""Весь период"", SYS_DB!$N$1, IFERROR(DATE(VALUE(LEFT($C$1,4)), VALUE(RIGHT($C$1,2)), 1), TODAY()))"
    wsDynM.Cells(2, 15).Formula = "=IF($C$1=""Весь период"", SYS_DB!$N$2, DATE(YEAR($O$1), MONTH($O$1)+1, 0))"

    wsDynM.Cells(3, 1).Value = "ИСТОРИЧЕСКАЯ ПОМЕСЯЧНАЯ ДИНАМИКА"
    wsDynM.Cells(3, 1).Font.Bold = True
    wsDynM.Cells(5, 1).Value = "Марка авто"
    wsDynM.Cells(5, 2).Value = "Месяц"
    wsDynM.Cells(5, 3).Value = "Кол-во продаж (шт)"
    wsDynM.Cells(5, 4).Value = "Средний чек (руб)"
    wsDynM.Cells(5, 5).Value = "ARPU (без НДС)"
    wsDynM.Cells(5, 6).Value = "Внесено предоплат (шт)"
    wsDynM.Range("A5:F5").Interior.Color = RGB(54, 96, 146)
    wsDynM.Range("A5:F5").Font.Color = RGB(255, 255, 255)
    wsDynM.Range("A5:F5").Font.Bold = True

    dmRow = 6
    If bCount > 0 And mCount > 0 Then
        For iSortL = 1 To bCount
            bN = brandNames(iSortL)
            For mIdxLocal = LBound(monthList) To UBound(monthList)
                hSales = dictHistSales(bN & "|" & monthList(mIdxLocal))
                wsDynM.Cells(dmRow, 1).Value = bN
                wsDynM.Cells(dmRow, 2).Value = monthList(mIdxLocal)
                wsDynM.Cells(dmRow, 3).Value = hSales
                If hSales > 0 Then
                    wsDynM.Cells(dmRow, 4).Value = Round(dictHistPrice(bN & "|" & monthList(mIdxLocal)) / hSales, 0)
                    wsDynM.Cells(dmRow, 5).Value = Round((dictHistComm(bN & "|" & monthList(mIdxLocal)) / hSales) / 1.22, 0)
                Else
                    wsDynM.Cells(dmRow, 4).Value = 0
                    wsDynM.Cells(dmRow, 5).Value = 0
                End If
                wsDynM.Cells(dmRow, 6).Value = dictHistPrepay(bN & "|" & monthList(mIdxLocal))
                dmRow = dmRow + 1
            Next mIdxLocal
        Next iSortL
    End If
    wsDynM.Range("A6:F" & dmRow - 1).Borders.LineStyle = xlContinuous
    wsDynM.Range("C6:F" & dmRow - 1).NumberFormat = "#,##0"

    wRow = dmRow + 2
    wsDynM.Cells(wRow, 1).Value = "ПОНЕДЕЛЬНОЕ СРАВНЕНИЕ (ДИНАМИЧЕСКИЙ ПЕРИОД)"
    wsDynM.Cells(wRow, 1).Font.Bold = True

    totalWeeks = DateDiff("w", minDate, maxDate, vbMonday) + 2
    If totalWeeks < 6 Then totalWeeks = 6
    If totalWeeks > 150 Then totalWeeks = 150

    hr1 = wRow + 10
    hr2 = wRow + 11

    For wIdx = 0 To totalWeeks - 1
        cLet = Split(wsDynM.Cells(1, wIdx + 2).Address(True, False), "$")(0)
        wsDynM.Cells(wRow + 1, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", ""Неделя "" & " & (wIdx + 1) & ")"

        If wIdx = 0 Then
            wsDynM.Cells(hr1, wIdx + 2).Formula = "=$O$1"
            wsDynM.Cells(hr2, wIdx + 2).Formula = "=MIN($O$2, " & cLet & "$" & hr1 & " + 7 - WEEKDAY(" & cLet & "$" & hr1 & ", 2))"
        Else
            pLet = Split(wsDynM.Cells(1, wIdx + 1).Address(True, False), "$")(0)
            wsDynM.Cells(hr1, wIdx + 2).Formula = "=IF(" & pLet & "$" & hr2 & "=0, 0, IF(" & pLet & "$" & hr2 & ">=$O$2, 0, " & pLet & "$" & hr2 & " + 1))"
            wsDynM.Cells(hr2, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, 0, MIN(" & cLet & "$" & hr1 & " + 6, $O$2))"
        End If
        wsDynM.Cells(wRow + 2, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", RIGHT(""0"" & DAY(" & cLet & "$" & hr1 & "), 2) & ""."" & RIGHT(""0"" & MONTH(" & cLet & "$" & hr1 & "), 2) & ""-"" & RIGHT(""0"" & DAY(" & cLet & "$" & hr2 & "), 2) & ""."" & RIGHT(""0"" & MONTH(" & cLet & "$" & hr2 & "), 2))"
    Next wIdx

    wMet = Array("ARPU китай", "ARPU Лада", "ARPU тотал", "Средний чек китай", "Средний чек лада", "Средний чек тотал")
    For iSortL = 0 To 5
        wsDynM.Cells(wRow + 3 + iSortL, 1).Value = wMet(iSortL)
    Next iSortL

    For wIdx = 0 To totalWeeks - 1
        cLet = Split(wsDynM.Cells(1, wIdx + 2).Address(True, False), "$")(0)
        ' Revenue-based ARPU formulas (use col Q = Revenue)
        wsDynM.Cells(wRow + 3, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""<>LADA"") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""<>LADA""), 0))"
        wsDynM.Cells(wRow + 4, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""LADA"") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""LADA""), 0))"
        wsDynM.Cells(wRow + 5, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & "), 0))"
        wsDynM.Cells(wRow + 6, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$F:$F, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""<>LADA"") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""<>LADA""), 0))"
        wsDynM.Cells(wRow + 7, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$F:$F, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""LADA"") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ", SYS_DB!$C:$C, ""LADA""), 0))"
        wsDynM.Cells(wRow + 8, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", IFERROR(SUMIFS(SYS_DB!$F:$F, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & ") / SUMIFS(SYS_DB!$E:$E, SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & "), 0))"
    Next wIdx

    lastColL = Split(wsDynM.Cells(1, totalWeeks + 1).Address(True, False), "$")(0)
    wsDynM.Range("B" & wRow + 1 & ":" & lastColL & wRow + 8).Borders.LineStyle = xlContinuous
    wsDynM.Range("B" & wRow + 3 & ":" & lastColL & wRow + 8).NumberFormat = "#,##0"

    wB2cRow = wRow + 13
    wsDynM.Cells(wB2cRow, 1).Value = "ПОНЕДЕЛЬНАЯ ДИНАМИКА ПО ТИПАМ СДЕЛОК B2C (шт.)"
    wsDynM.Cells(wB2cRow, 1).Font.Bold = True
    wsDynM.Range(wsDynM.Cells(wRow + 1, 2), wsDynM.Cells(wRow + 2, totalWeeks + 1)).Copy Destination:=wsDynM.Cells(wB2cRow + 1, 2)
    wsDynM.Range(wsDynM.Cells(wB2cRow + 1, 2), wsDynM.Cells(wB2cRow + 2, totalWeeks + 1)).Font.Bold = True

    b2cListRow = wB2cRow + 3
    If b2cCount > 0 Then
        For iSortL = 1 To b2cCount
            wsDynM.Cells(b2cListRow, 1).Value = b2cNames(iSortL)
            For wIdx = 0 To totalWeeks - 1
                cLet = Split(wsDynM.Cells(1, wIdx + 2).Address(True, False), "$")(0)
                wsDynM.Cells(b2cListRow, wIdx + 2).Formula = "=IF(" & cLet & "$" & hr1 & "=0, """", SUMIFS(SYS_DB!$E:$E, SYS_DB!$D:$D, $A" & b2cListRow & ", SYS_DB!$K:$K, "">=""&" & cLet & "$" & hr1 & ", SYS_DB!$K:$K, ""<=""&" & cLet & "$" & hr2 & "))"
            Next wIdx
            b2cListRow = b2cListRow + 1
        Next iSortL
        wsDynM.Range("B" & wB2cRow + 3 & ":" & lastColL & b2cListRow - 1).NumberFormat = "#,##0"
        wsDynM.Range("B" & wB2cRow + 1 & ":" & lastColL & b2cListRow - 1).Borders.LineStyle = xlContinuous
    End If
    wsDynM.Rows(hr1 & ":" & hr2).Hidden = True
    wsDynM.Columns("A:" & lastColL).AutoFit

    wsDynM.Calculate
    Call RefreshWeeklyView

    ' =========================================================================
    ' === DYNAMICS SHEET (OPERATIONAL) ===
    ' =========================================================================
    wsDyn.Activate
    wsDyn.Cells(1, 1).Value = "ВЫБЕРИТЕ МЕСЯЦ ДЛЯ АНАЛИЗА ->"
    wsDyn.Cells(1, 1).Font.Bold = True
    With wsDyn.Cells(1, 3)
        .NumberFormat = "@"
        .Value = maxMKeyString
        .Interior.Color = RGB(255, 255, 204)
        .Font.Bold = True
        .Borders.LineStyle = xlContinuous
        If mCount > 0 Then
            .Validation.Delete
            .Validation.Add Type:=xlValidateList, Formula1:="=SYS_DB!$M$1:$M$" & lastMRowLocal
        End If
    End With

    wsDyn.Cells(3, 1).Value = "ОПЕРАТИВНАЯ ДИНАМИКА БРЕНДОВ"
    wsDyn.Cells(3, 1).Font.Bold = True
    wsDyn.Cells(5, 1).Value = "Показатель"
    wsDyn.Cells(5, 2).Value = "Период"
    wsDyn.Cells(5, 3).Value = "Тотал"

    colIdxL = 4
    If bCount > 0 Then
        For iSortL = 1 To bCount
            wsDyn.Cells(5, colIdxL).Value = brandNames(iSortL)
            colIdxL = colIdxL + 1
        Next iSortL
    End If

    dRow = 6
    labelsMetrics = Array("Кол-во продаж (шт.)", "Средний чек (руб.)", "ARPU (без НДС, руб.)", "Кол-во предоплат (шт.)")
    labelsPeriods = Array("Прошлая неделя (календарь)", "Выбранный месяц (фильтр сверху)")

    For mLabel = 0 To 3
        For pLabel = 0 To 1
            wsDyn.Cells(dRow, 1).Value = labelsMetrics(mLabel)
            wsDyn.Cells(dRow, 2).Value = labelsPeriods(pLabel)

            If pLabel = 0 Then
                tWS = 0: tWP = 0: tWC = 0: tWPrep = 0
                For Each mk In dictBrands.Keys
                    tWS = tWS + dictWeekSales(mk)
                    tWP = tWP + dictWeekPrice(mk)
                    tWC = tWC + dictWeekComm(mk)
                    tWPrep = tWPrep + dictWeekPrepay(mk)
                Next mk

                Select Case mLabel
                    Case 0: wsDyn.Cells(dRow, 3).Value = tWS
                    Case 1: If tWS > 0 Then wsDyn.Cells(dRow, 3).Value = Round(tWP / tWS, 0) Else wsDyn.Cells(dRow, 3).Value = 0
                    Case 2: If tWS > 0 Then wsDyn.Cells(dRow, 3).Value = Round((tWC / tWS) / 1.22, 0) Else wsDyn.Cells(dRow, 3).Value = 0
                    Case 3: wsDyn.Cells(dRow, 3).Value = tWPrep
                End Select
            Else
                Select Case mLabel
                    Case 0: wsDyn.Cells(dRow, 3).Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1)"
                    Case 1: wsDyn.Cells(dRow, 3).Formula = "=IFERROR(SUMIFS(SYS_DB!$F:$F, SYS_DB!$A:$A, $C$1) / SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1), 0)"
                    Case 2: wsDyn.Cells(dRow, 3).Formula = "=IFERROR(SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$A:$A, $C$1) / SUMIFS(SYS_DB!$E:$E, SYS_DB!$A:$A, $C$1), 0)"
                    Case 3: wsDyn.Cells(dRow, 3).Formula = "=SUMIFS(SYS_DB!$H:$H, SYS_DB!$B:$B, $C$1)"
                End Select
            End If

            colIdxL = 4
            If bCount > 0 Then
                For iSortL = 1 To bCount
                    aBr = wsDyn.Cells(5, colIdxL).Address(True, False)
                    curBr = brandNames(iSortL)

                    If pLabel = 0 Then
                        Select Case mLabel
                            Case 0: wsDyn.Cells(dRow, colIdxL).Value = dictWeekSales(curBr)
                            Case 1: If dictWeekSales(curBr) > 0 Then wsDyn.Cells(dRow, colIdxL).Value = Round(dictWeekPrice(curBr) / dictWeekSales(curBr), 0) Else wsDyn.Cells(dRow, colIdxL).Value = 0
                            Case 2: If dictWeekSales(curBr) > 0 Then wsDyn.Cells(dRow, colIdxL).Value = Round((dictWeekComm(curBr) / dictWeekSales(curBr)) / 1.22, 0) Else wsDyn.Cells(dRow, colIdxL).Value = 0
                            Case 3: wsDyn.Cells(dRow, colIdxL).Value = dictWeekPrepay(curBr)
                        End Select
                    Else
                        Select Case mLabel
                            Case 0: wsDyn.Cells(dRow, colIdxL).Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$A:$A, $C$1)"
                            Case 1: wsDyn.Cells(dRow, colIdxL).Formula = "=IFERROR(SUMIFS(SYS_DB!$F:$F, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$A:$A, $C$1) / SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$A:$A, $C$1), 0)"
                            Case 2: wsDyn.Cells(dRow, colIdxL).Formula = "=IFERROR(SUMIFS(SYS_DB!$Q:$Q, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$A:$A, $C$1) / SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$A:$A, $C$1), 0)"
                            Case 3: wsDyn.Cells(dRow, colIdxL).Formula = "=SUMIFS(SYS_DB!$H:$H, SYS_DB!$C:$C, " & aBr & ", SYS_DB!$B:$B, $C$1)"
                        End Select
                    End If
                    colIdxL = colIdxL + 1
                Next iSortL
            End If
            dRow = dRow + 1
        Next pLabel
    Next mLabel

    wsDyn.Range(wsDyn.Cells(5, 1), wsDyn.Cells(5, colIdxL - 1)).Interior.Color = RGB(54, 96, 146)
    wsDyn.Range(wsDyn.Cells(5, 1), wsDyn.Cells(5, colIdxL - 1)).Font.Color = RGB(255, 255, 255)
    wsDyn.Range(wsDyn.Cells(5, 1), wsDyn.Cells(5, colIdxL - 1)).Font.Bold = True
    wsDyn.Range(wsDyn.Cells(5, 1), wsDyn.Cells(dRow - 1, colIdxL - 1)).Borders.LineStyle = xlContinuous
    wsDyn.Range(wsDyn.Cells(6, 3), wsDyn.Cells(dRow - 1, colIdxL - 1)).NumberFormat = "#,##0"

    b2cStart = dRow + 2
    wsDyn.Cells(b2cStart - 1, 1).Value = "ТИП СДЕЛКИ (B2C) ПО МАРКАМ ЗА ВЫБРАННЫЙ МЕСЯЦ"
    wsDyn.Cells(b2cStart - 1, 1).Font.Bold = True
    wsDyn.Cells(b2cStart, 1).Value = "Тип сделки.B2C"
    wsDyn.Cells(b2cStart, 3).Value = "Тотал"

    colIdxL = 4
    If bCount > 0 Then
        For iSortL = 1 To bCount
            wsDyn.Cells(b2cStart, colIdxL).Value = brandNames(iSortL)
            colIdxL = colIdxL + 1
        Next iSortL
    End If

    wsDyn.Range(wsDyn.Cells(b2cStart, 1), wsDyn.Cells(b2cStart, colIdxL - 1)).Interior.Color = RGB(54, 96, 146)
    wsDyn.Range(wsDyn.Cells(b2cStart, 1), wsDyn.Cells(b2cStart, colIdxL - 1)).Font.Color = RGB(255, 255, 255)

    cRow = b2cStart + 1
    If b2cCount > 0 Then
        For iSortL = 1 To b2cCount
            wsDyn.Cells(cRow, 1).Value = b2cNames(iSortL)
            aB2C = wsDyn.Cells(cRow, 1).Address(False, True)
            wsDyn.Cells(cRow, 3).Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$D:$D, " & aB2C & ", SYS_DB!$A:$A, $C$1)"

            colIdxL = 4
            For bIdx = 1 To bCount
                wsDyn.Cells(cRow, colIdxL).Formula = "=SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & wsDyn.Cells(b2cStart, colIdxL).Address(True, False) & ", SYS_DB!$D:$D, " & aB2C & ", SYS_DB!$A:$A, $C$1)"
                colIdxL = colIdxL + 1
            Next bIdx
            cRow = cRow + 1
        Next iSortL
    End If

    wsDyn.Cells(cRow, 1).Value = "ИТОГО (шт.)"
    wsDyn.Cells(cRow, 3).Formula = "=SUM(C" & b2cStart + 1 & ":C" & cRow - 1 & ")"

    shareRow = cRow + 1
    wsDyn.Cells(shareRow, 1).Value = "Доля бренда"
    wsDyn.Cells(shareRow, 3).Value = 1

    colIdxL = 4
    For bIdx = 1 To bCount
        wsDyn.Cells(cRow, colIdxL).Formula = "=SUM(" & wsDyn.Cells(b2cStart + 1, colIdxL).Address(False, False) & ":" & wsDyn.Cells(cRow - 1, colIdxL).Address(False, False) & ")"
        wsDyn.Cells(shareRow, colIdxL).Formula = "=IF($C$" & cRow & "=0, 0, " & wsDyn.Cells(cRow, colIdxL).Address(False, False) & " / $C$" & cRow & ")"
        colIdxL = colIdxL + 1
    Next bIdx

    wsDyn.Range(wsDyn.Cells(b2cStart, 1), wsDyn.Cells(shareRow, colIdxL - 1)).Borders.LineStyle = xlContinuous
    wsDyn.Range(wsDyn.Cells(b2cStart + 1, 3), wsDyn.Cells(cRow, colIdxL - 1)).NumberFormat = "#,##0"
    wsDyn.Range(wsDyn.Cells(shareRow, 3), wsDyn.Cells(shareRow, colIdxL - 1)).NumberFormat = "0%"

    wsDyn.Range(wsDyn.Cells(cRow, 1), wsDyn.Cells(cRow, colIdxL - 1)).Interior.Color = RGB(146, 208, 80)
    wsDyn.Range(wsDyn.Cells(cRow, 1), wsDyn.Cells(cRow, colIdxL - 1)).Font.Bold = True
    wsDyn.Range(wsDyn.Cells(shareRow, 1), wsDyn.Cells(shareRow, colIdxL - 1)).Interior.Color = RGB(220, 230, 241)
    wsDyn.Range(wsDyn.Cells(shareRow, 1), wsDyn.Cells(shareRow, colIdxL - 1)).Font.Bold = True

    pStart = shareRow + 3
    wsDyn.Cells(pStart - 1, 1).Value = "СТРУКТУРА СДЕЛОК B2C ВНУТРИ БРЕНДА (%)"
    wsDyn.Cells(pStart - 1, 1).Font.Bold = True
    wsDyn.Range(wsDyn.Cells(b2cStart, 1), wsDyn.Cells(b2cStart, colIdxL - 1)).Copy Destination:=wsDyn.Cells(pStart, 1)

    prRow = pStart + 1
    If b2cCount > 0 Then
        For iSortL = 1 To b2cCount
            wsDyn.Cells(prRow, 1).Value = b2cNames(iSortL)
            wsDyn.Cells(prRow, 3).Formula = "=IF(C$" & cRow & "=0, 0, C" & (b2cStart + iSortL) & " / C$" & cRow & ")"
            colIdxL = 4
            For bIdx = 1 To bCount
                wsDyn.Cells(prRow, colIdxL).Formula = "=IF(" & wsDyn.Cells(cRow, colIdxL).Address(False, False) & "=0, 0, " & wsDyn.Cells(b2cStart + iSortL, colIdxL).Address(False, False) & " / " & wsDyn.Cells(cRow, colIdxL).Address(False, False) & ")"
                colIdxL = colIdxL + 1
            Next bIdx
            prRow = prRow + 1
        Next iSortL
    End If

    wsDyn.Range(wsDyn.Cells(pStart + 1, 3), wsDyn.Cells(prRow - 1, colIdxL - 1)).NumberFormat = "0%"
    wsDyn.Range(wsDyn.Cells(pStart, 1), wsDyn.Cells(prRow - 1, colIdxL - 1)).Borders.LineStyle = xlContinuous

    rrStart = prRow + 2
    wsDyn.Cells(rrStart, 1).Value = "RUN RATE (ПРОГНОЗ ПРОДАЖ ДО КОНЦА МЕСЯЦА)"
    wsDyn.Cells(rrStart, 1).Font.Bold = True

    wsDyn.Range("Z1").Formula = "=IF($C$1=""Весь период"", 1, IF(EOMONTH(DATE(VALUE(LEFT($C$1,4)), VALUE(RIGHT($C$1,2)), 1), 0) <> EOMONTH(TODAY(), 0), 1, (DAY(EOMONTH(TODAY(),0)) + 0.9) / IF(DAY(TODAY()) <= DAY(EOMONTH(TODAY(),0)) - 3, DAY(TODAY()), (DAY(EOMONTH(TODAY(),0)) - 3) + (DAY(TODAY()) - (DAY(EOMONTH(TODAY(),0)) - 3)) * 1.3)))"
    wsDyn.Range("Z1").Font.Color = RGB(255, 255, 255)

    rrStart = rrStart + 1
    wsDyn.Cells(rrStart, 1).Value = "Бренд \ Тип B2C"
    wsDyn.Cells(rrStart, 1).Font.Bold = True
    wsDyn.Cells(rrStart, 1).Interior.Color = RGB(54, 96, 146)
    wsDyn.Cells(rrStart, 1).Font.Color = RGB(255, 255, 255)

    cCol = 2
    For bIdx = 1 To b2cCount
        wsDyn.Cells(rrStart, cCol).Value = b2cNames(bIdx)
        wsDyn.Cells(rrStart, cCol).Font.Bold = True
        wsDyn.Cells(rrStart, cCol).Interior.Color = RGB(54, 96, 146)
        wsDyn.Cells(rrStart, cCol).Font.Color = RGB(255, 255, 255)
        cCol = cCol + 1
    Next bIdx

    wsDyn.Cells(rrStart, cCol).Value = "Итого прогноз"
    wsDyn.Cells(rrStart, cCol).Font.Bold = True
    wsDyn.Cells(rrStart, cCol).Interior.Color = RGB(54, 96, 146)
    wsDyn.Cells(rrStart, cCol).Font.Color = RGB(255, 255, 255)

    rRow = rrStart + 1
    For iSortL = 1 To bCount
        wsDyn.Cells(rRow, 1).Value = brandNames(iSortL)
        bNameCell = wsDyn.Cells(rRow, 1).Address(False, True)

        For bIdx = 1 To b2cCount
            b2cNameCell = wsDyn.Cells(rrStart, bIdx + 1).Address(True, False)
            wsDyn.Cells(rRow, bIdx + 1).Formula = "=ROUND(IF($C$1=""Весь период"", SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & bNameCell & ", SYS_DB!$D:$D, " & b2cNameCell & ") * $Z$1, SUMIFS(SYS_DB!$E:$E, SYS_DB!$C:$C, " & bNameCell & ", SYS_DB!$D:$D, " & b2cNameCell & ", SYS_DB!$A:$A, $C$1) * $Z$1), 0)"
        Next bIdx
        wsDyn.Cells(rRow, cCol).Formula = "=SUM(" & wsDyn.Cells(rRow, 2).Address(False, False) & ":" & wsDyn.Cells(rRow, cCol - 1).Address(False, False) & ")"
        rRow = rRow + 1
    Next iSortL

    wsDyn.Cells(rRow, 1).Value = "ИТОГО"
    For bIdx = 1 To b2cCount
        wsDyn.Cells(rRow, bIdx + 1).Formula = "=SUM(" & wsDyn.Cells(rrStart + 1, bIdx + 1).Address(False, False) & ":" & wsDyn.Cells(rRow - 1, bIdx + 1).Address(False, False) & ")"
    Next bIdx
    wsDyn.Cells(rRow, cCol).Formula = "=SUM(" & wsDyn.Cells(rrStart + 1, cCol).Address(False, False) & ":" & wsDyn.Cells(rRow - 1, cCol).Address(False, False) & ")"

    wsDyn.Range(wsDyn.Cells(rrStart, 1), wsDyn.Cells(rRow, cCol)).Borders.LineStyle = xlContinuous
    wsDyn.Range(wsDyn.Cells(rRow, 1), wsDyn.Cells(rRow, cCol)).Font.Bold = True
    wsDyn.Range(wsDyn.Cells(rRow, 1), wsDyn.Cells(rRow, cCol)).Interior.Color = RGB(146, 208, 80)
    wsDyn.Range(wsDyn.Cells(rrStart + 1, 2), wsDyn.Cells(rRow, cCol)).NumberFormat = "#,##0"
    wsDyn.Columns("A:AZ").AutoFit

    ' =========================================================================
    ' === MANAGERS SHEET ===
    ' =========================================================================
    wsMgr.Activate
    wsMgr.Cells(1, 1).Value = "ФИЛЬТР ДАННЫХ ->"
    wsMgr.Cells(1, 1).Font.Bold = True
    With wsMgr.Cells(1, 3)
        .NumberFormat = "@"
        .Value = maxMKeyString
        .Interior.Color = RGB(255, 255, 204)
        .Font.Bold = True
        .Borders.LineStyle = xlContinuous
        If mCount > 0 Then
            .Validation.Delete
            .Validation.Add Type:=xlValidateList, Formula1:="=SYS_DB!$M$1:$M$" & lastMRowLocal
        End If
    End With

    Set dictSeniors = CreateObject("Scripting.Dictionary")

    For Each mk In dictAllMgrs.Keys
        sen = dictMgrSenior(CStr(mk))
        If Not dictSeniors.Exists(sen) Then
            Set dictSeniors(sen) = CreateObject("Scripting.Dictionary")
        End If
        dictSeniors(sen)(CStr(mk)) = dictMgrSalesAll(CStr(mk))
    Next mk

    mRow = 4

    For Each mk In dictSeniors.Keys
        sen = CStr(mk)
        wsMgr.Cells(mRow, 1).Value = "Группа: " & sen
        wsMgr.Cells(mRow, 1).Font.Bold = True
        wsMgr.Cells(mRow, 1).Font.Size = 12
        mRow = mRow + 1

        startT = mRow
        wsMgr.Cells(mRow, 1).Value = "Менеджер"
        wsMgr.Cells(mRow, 2).Value = "Продажи"
        wsMgr.Cells(mRow, 3).Value = "Предоплаты"
        wsMgr.Range(wsMgr.Cells(mRow, 1), wsMgr.Cells(mRow, 3)).Interior.Color = RGB(54, 96, 146)
        wsMgr.Range(wsMgr.Cells(mRow, 1), wsMgr.Cells(mRow, 3)).Font.Color = RGB(255, 255, 255)
        wsMgr.Range(wsMgr.Cells(mRow, 1), wsMgr.Cells(mRow, 3)).Font.Bold = True
        mRow = mRow + 1

        Set gMgrs = dictSeniors(sen)
        gCount = gMgrs.Count
        ReDim arrM(1 To gCount)
        ReDim arrMS(1 To gCount)

        idx2 = 1
        For Each k In gMgrs.Keys
            arrM(idx2) = CStr(k)
            arrMS(idx2) = gMgrs(k)
            idx2 = idx2 + 1
        Next k

        For iSortL = 1 To gCount - 1
            For jSortL = iSortL + 1 To gCount
                If arrMS(iSortL) < arrMS(jSortL) Then
                    tempNumLocal = arrMS(iSortL)
                    arrMS(iSortL) = arrMS(jSortL)
                    arrMS(jSortL) = tempNumLocal

                    tempStrLocal = arrM(iSortL)
                    arrM(iSortL) = arrM(jSortL)
                    arrM(jSortL) = tempStrLocal
                End If
            Next jSortL
        Next iSortL

        For iSortL = 1 To gCount
            wsMgr.Cells(mRow, 1).Value = arrM(iSortL)
            wsMgr.Cells(mRow, 2).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB!$E:$E, SYS_DB!$L:$L, $A" & mRow & "), SUMIFS(SYS_DB!$E:$E, SYS_DB!$L:$L, $A" & mRow & ", SYS_DB!$A:$A, $C$1))"
            wsMgr.Cells(mRow, 3).Formula = "=IF($C$1=""Весь период"", SUMIFS(SYS_DB!$H:$H, SYS_DB!$L:$L, $A" & mRow & "), SUMIFS(SYS_DB!$H:$H, SYS_DB!$L:$L, $A" & mRow & ", SYS_DB!$B:$B, $C$1))"
            mRow = mRow + 1
        Next iSortL

        wsMgr.Cells(mRow, 1).Value = "ИТОГО (" & sen & ")"
        wsMgr.Cells(mRow, 2).Formula = "=SUM(B" & startT + 1 & ":B" & (mRow - 1) & ")"
        wsMgr.Cells(mRow, 3).Formula = "=SUM(C" & startT + 1 & ":C" & (mRow - 1) & ")"
        wsMgr.Range(wsMgr.Cells(mRow, 1), wsMgr.Cells(mRow, 3)).Font.Bold = True
        wsMgr.Range(wsMgr.Cells(mRow, 1), wsMgr.Cells(mRow, 3)).Interior.Color = RGB(146, 208, 80)
        wsMgr.Range(wsMgr.Cells(startT, 1), wsMgr.Cells(mRow, 3)).Borders.LineStyle = xlContinuous
        mRow = mRow + 2
    Next mk
    wsMgr.Columns("A:G").AutoFit
End Sub
