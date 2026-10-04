// Deployment requires Google owner access and migration of calculator event sending to a trusted backend.
/**
 * Google Apps Script — Web App для аналитики СберАвто.
 *
 * ВАЖНО: CLICK_GROUP / SEARCH_EMPTY_CITY можно оставлять на ГЛАВНОМ листе.
 * B2B-статистика читает их через doGet(?scope=b2b) — отдельная вкладка НЕ нужна.
 *
 * После вставки: Развернуть → Управление развёртываниями → Изменить → Новая версия → Развернуть.
 * URL в 3_script.js (API_URL) = URL этого развёртывания.
 */

var ANALYTICS_SHEET_NAME = "Аналитика_Поиска";
var B2B_ACTIONS = { SEARCH_EMPTY_CITY: true, CLICK_GROUP: true };

function getMainSheet_(ss) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getName() !== ANALYTICS_SHEET_NAME) {
      return sheets[i];
    }
  }
  return ss.getActiveSheet();
}

function getOrCreateAnalyticsSheet_(ss) {
  var sheet = ss.getSheetByName(ANALYTICS_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(ANALYTICS_SHEET_NAME);
    sheet.appendRow([
      "timestamp", "managerId", "managerName", "clientId",
      "action", "details", "clientLink"
    ]);
  }
  return sheet;
}

function isDirectoryAnalyticsAction_(action, dest) {
  action = String(action || "").trim();
  dest = String(dest || "").trim().toLowerCase();
  if (dest === "analytics") return true;
  return !!B2B_ACTIONS[action];
}

function response_(value) {
  return ContentService.createTextOutput(JSON.stringify(value)).setMimeType(ContentService.MimeType.JSON);
}
function authorized_(provided, property) {
  var expected = PropertiesService.getScriptProperties().getProperty(property);
  if (!expected || expected.length < 32 || typeof provided !== 'string' || provided.length !== expected.length) return false;
  var diff = 0;
  for (var i=0;i<expected.length;i++) diff |= expected.charCodeAt(i)^provided.charCodeAt(i);
  return diff === 0;
}
// Raw analytics are never returned by GET, including old ?scope=b2b callers.
function doGet(e) { return response_({error:'unauthorized'}); }
function doPost(e) {
  var params = e && e.parameter || {};
  if (params.operation === 'export') {
    if (!authorized_(params.token, 'ANALYTICS_READ_TOKEN')) return response_({error:'unauthorized'});
    return exportRows_(e);
  }
  // Only the authenticated calculator backend may send events. Never put this token in browser JS.
  if (!authorized_(params.token, 'ANALYTICS_WRITE_TOKEN')) return response_({error:'unauthorized'});
  var fields = ['managerId','managerName','clientId','action','details','clientLink'];
  if (!params.managerId || !params.action) return response_({error:'invalid_event'});
  for (var i=0;i<fields.length;i++) if (String(params[fields[i]] || '').length > 2000) return response_({error:'invalid_event'});
  var lock = LockService.getScriptLock();
  if (!lock.tryLock(5000)) return response_({error:'busy'});
  try {
    var row = [new Date().toISOString()];
    for (var j=0;j<fields.length;j++) {
      var value=String(params[fields[j]] || '');
      row.push(/^[=+@\-]/.test(value) ? "'"+value : value);
    }
    getMainSheet_(SpreadsheetApp.getActiveSpreadsheet()).appendRow(row);
    return response_({success:true});
  } catch (_) { return response_({error:'unavailable'}); }
  finally {lock.releaseLock();}
}

function rowToObj_(row) {
  return {
    timestamp: row[0] ? String(row[0]) : "",
    managerId: row[1] ? String(row[1]) : "",
    managerName: row[2] ? String(row[2]) : "",
    clientId: row[3] ? String(row[3]) : "",
    action: row[4] ? String(row[4]) : "",
    details: row[5] ? String(row[5]) : "",
    clientLink: row[6] ? String(row[6]) : ""
  };
}

function isHeaderRow_(row) {
  var a = String(row[4] || "").toLowerCase();
  return a === "action" || a === "действие";
}

/**
 * Читает лист. Если onlyB2b=true — только SEARCH_EMPTY_CITY / CLICK_GROUP
 * (с главного листа или с Аналитика_Поиска — без разницы).
 */
function appendSheetRowsToData_(sheet, data, onlyB2b) {
  if (!sheet) return;
  var rows = sheet.getDataRange().getValues();
  if (!rows || rows.length < 1) return;

  var start = isHeaderRow_(rows[0]) ? 1 : 0;
  for (var i = start; i < rows.length; i++) {
    var obj = rowToObj_(rows[i]);
    var action = String(obj.action || "").trim();
    if (onlyB2b && !B2B_ACTIONS[action]) continue;
    if (!action) continue;
    data.push(obj);
  }
}

function exportRows_(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var data = [];
    var params = (e && e.parameter) ? e.parameter : {};
    var onlyB2b = String(params.scope || "").toLowerCase() === "b2b";

    // 1) Главный лист — основной источник (сюда сейчас пишутся клики/пустые города)
    var mainSheet = getMainSheet_(ss);
    appendSheetRowsToData_(mainSheet, data, onlyB2b);

    // 2) Аналитика_Поиска — если когда-нибудь появится, тоже подхватим
    var analyticsSheet = ss.getSheetByName(ANALYTICS_SHEET_NAME);
    if (analyticsSheet && analyticsSheet.getSheetId() !== mainSheet.getSheetId()) {
      appendSheetRowsToData_(analyticsSheet, data, onlyB2b);
    }

    return ContentService
      .createTextOutput(JSON.stringify(data))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: "unavailable" }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
