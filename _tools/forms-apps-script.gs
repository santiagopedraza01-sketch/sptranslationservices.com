/**
 * SP Translations — form endpoint (Google Apps Script web app).
 *
 * Receives the website's quote, review and contact forms (app.js posts JSON here),
 * and for every submission:
 *   1. saves any attached files to Google Drive, in "SP Translations — Form uploads/<date> — <name>"
 *   2. logs a row in the Google Sheet "SP Translations — Form log" (a backup of every request)
 *   3. emails NOTIFY_TO, with Reply-To set to the client, the files attached when they
 *      fit in an email, and always a link to the Drive folder.
 *
 * SET UP (once, signed in as santiagopedraza01@gmail.com) — see SANTIAGO-README.md:
 *   script.google.com → New project → paste this file → Save → run "setup" once and allow
 *   access → Deploy → New deployment → Web app → Execute as: Me, Who has access: Anyone →
 *   Deploy → copy the Web app URL (ends in /exec) into the forms' action attribute.
 * After editing this script: Deploy → Manage deployments → Edit → Version: New version,
 * so the same URL keeps working.
 */

var NOTIFY_TO = 'santiagopedraza01@gmail.com';
var SITE = 'sptranslationservices.com';
var MAX_TOTAL_BYTES = 20 * 1024 * 1024;     // matches the limit shown on the quote form
var ATTACH_LIMIT_BYTES = 18 * 1024 * 1024;  // above this, the email links to Drive instead of attaching
var MAX_FILES = 20;

var SUBJECTS = {
  docket: 'New quote request',
  reviewForm: 'New client review',
  contactForm: 'New contact message'
};

function doPost(e) {
  var data, row = { when: new Date() };
  try {
    data = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    var fields = data.fields || {};
    if (fields._honey) return json_({ ok: true });            // spam trap filled in: drop silently

    var files = (data.files || []).slice(0, MAX_FILES);
    var total = files.reduce(function (n, f) { return n + (f.size || 0); }, 0);
    if (total > MAX_TOTAL_BYTES) return json_({ ok: false, error: 'too_large' });

    var name = clean_(fields.name || '') || 'Website visitor';
    var email = clean_(fields.email || '');
    var subject = (SUBJECTS[data.form] || 'New website message') + ' — ' + name + ' — ' + SITE;
    row.form = data.form || ''; row.name = name; row.email = email;

    // 1. Files to Drive
    var folder = null, blobs = [], links = [];
    if (files.length) {
      folder = root_().createFolder(Utilities.formatDate(row.when, 'Europe/Malta', 'yyyy-MM-dd HHmm') + ' — ' + name);
      files.forEach(function (f) {
        var blob = Utilities.newBlob(Utilities.base64Decode(f.data), f.type || 'application/octet-stream', clean_(f.name) || 'file');
        var file = folder.createFile(blob);
        blobs.push(blob);
        links.push({ name: file.getName(), url: file.getUrl(), size: f.size || 0 });
      });
      row.folder = folder.getUrl();
    }

    // 2. Log
    log_(row, fields, links);

    // 3. Email
    var rows = Object.keys(fields).filter(function (k) {
      return k.charAt(0) !== '_' && k !== 'consent' && String(fields[k]).trim() !== '';
    }).map(function (k) { return [label_(k), String(fields[k])]; });
    if (data.page) rows.push(['Sent from', data.page]);

    var html = '<h2 style="font-family:Georgia,serif;font-weight:normal">' + esc_(SUBJECTS[data.form] || 'New website message') + '</h2>' +
      '<table cellpadding="8" style="border-collapse:collapse;font-family:Arial,sans-serif;font-size:14px">' +
      rows.map(function (r) {
        return '<tr><th align="left" valign="top" style="border-bottom:1px solid #eee;color:#555;white-space:nowrap">' + esc_(r[0]) +
               '</th><td style="border-bottom:1px solid #eee">' + esc_(r[1]).replace(/\n/g, '<br>') + '</td></tr>';
      }).join('') + '</table>';
    if (links.length) {
      html += '<h3 style="font-family:Arial,sans-serif">Files (' + links.length + ')</h3><ul style="font-family:Arial,sans-serif;font-size:14px">' +
        links.map(function (l) { return '<li><a href="' + l.url + '">' + esc_(l.name) + '</a> (' + size_(l.size) + ')</li>'; }).join('') +
        '</ul><p style="font-family:Arial,sans-serif;font-size:14px"><a href="' + folder.getUrl() + '">Open the folder in Google Drive</a></p>';
    }
    if (email) html += '<p style="font-family:Arial,sans-serif;font-size:13px;color:#777">Reply to this email to answer ' + esc_(name) + ' directly.</p>';

    var plain = rows.map(function (r) { return r[0] + ': ' + r[1]; }).join('\n') +
      (links.length ? '\n\nFiles:\n' + links.map(function (l) { return '- ' + l.name + ': ' + l.url; }).join('\n') : '');

    var opts = { htmlBody: html, name: 'SP Translations website' };
    if (email) opts.replyTo = email;
    if (blobs.length && total <= ATTACH_LIMIT_BYTES) opts.attachments = blobs;
    MailApp.sendEmail(NOTIFY_TO, subject, plain, opts);

    return json_({ ok: true });
  } catch (err) {
    try { row.error = String(err); log_(row, (data && data.fields) || {}, []); } catch (ignore) {}
    return json_({ ok: false, error: String(err) });
  }
}

/** Opening the web-app URL in a browser shows this, so you can check it is live. */
function doGet() {
  return ContentService.createTextOutput('SP Translations form endpoint is running.');
}

/** Run once from the editor: grants access, creates the Drive folder and the log sheet, and sends a test email. */
function setup() {
  root_(); sheet_();
  MailApp.sendEmail(NOTIFY_TO, 'Form endpoint ready — ' + SITE,
    'The website form endpoint is set up. Uploads go to the Drive folder "SP Translations — Form uploads", ' +
    'and every request is logged in the Google Sheet "SP Translations — Form log".');
}

function root_() {
  var props = PropertiesService.getScriptProperties(), id = props.getProperty('ROOT_ID');
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) {} }
  var f = DriveApp.createFolder('SP Translations — Form uploads');
  props.setProperty('ROOT_ID', f.getId());
  return f;
}

function sheet_() {
  var props = PropertiesService.getScriptProperties(), id = props.getProperty('SHEET_ID'), ss;
  if (id) { try { ss = SpreadsheetApp.openById(id); } catch (e) {} }
  if (!ss) {
    ss = SpreadsheetApp.create('SP Translations — Form log');
    ss.getSheets()[0].appendRow(['Received', 'Form', 'Name', 'Email', 'Details', 'Files', 'Drive folder', 'Error']);
    ss.getSheets()[0].setFrozenRows(1);
    props.setProperty('SHEET_ID', ss.getId());
  }
  return ss.getSheets()[0];
}

function log_(row, fields, links) {
  var details = Object.keys(fields).filter(function (k) { return k.charAt(0) !== '_'; })
    .map(function (k) { return label_(k) + ': ' + fields[k]; }).join('\n');
  sheet_().appendRow([row.when, row.form || '', row.name || '', row.email || '', details,
    links.map(function (l) { return l.name; }).join(', '), row.folder || '', row.error || '']);
}

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function clean_(s) { return String(s || '').replace(/[\r\n\t]+/g, ' ').replace(/[\\/:*?"<>|]+/g, '-').trim().slice(0, 120); }
function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
function size_(b) { return b < 1048576 ? Math.max(1, Math.round(b / 1024)) + ' KB' : (b / 1048576).toFixed(1) + ' MB'; }
function label_(k) {
  var L = { publish_consent: 'May publish', translated: 'Document translated' };
  if (L[k]) return L[k];
  k = k.replace(/[_-]+/g, ' ').replace(/([a-z])([A-Z])/g, '$1 $2');
  return k.charAt(0).toUpperCase() + k.slice(1);
}
