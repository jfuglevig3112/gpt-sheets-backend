{\rtf1\ansi\ansicpg1252\cocoartf2708
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import json\
from flask import Flask, request, jsonify\
import gspread\
from google.oauth2.service_account import Credentials\
from gspread.exceptions import WorksheetNotFound\
\
app = Flask(__name__)\
\
\
def get_gspread_client():\
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])\
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]\
    creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)\
    return gspread.authorize(creds)\
\
\
@app.route("/health", methods=["GET"])\
def health():\
    return jsonify(\{"status": "ok"\})\
\
\
@app.route("/write-to-sheets", methods=["POST"])\
def write_to_sheets():\
    data = request.get_json(force=True)\
\
    # Forventet payload:\
    # \{\
    #   "sheet_id": "...",\
    #   "tab": "Ark 1",\
    #   "rows": [\
    #       ["kol1", "kol2"],\
    #       ["val1", "val2"]\
    #   ]\
    # \}\
\
    sheet_id = data["sheet_id"]\
    tab_name = data["tab"]\
    rows = data["rows"]\
\
    gc = get_gspread_client()\
    sh = gc.open_by_key(sheet_id)\
\
    try:\
        ws = sh.worksheet(tab_name)\
    except WorksheetNotFound:\
        ws = sh.add_worksheet(title=tab_name, rows="1000", cols="26")\
\
    for row in rows:\
        ws.append_row(row, value_input_option="USER_ENTERED")\
\
    return jsonify(\{\
        "status": "ok",\
        "rows_written": len(rows),\
        "tab": tab_name\
    \}), 200\
\
\
if __name__ == "__main__":\
    port = int(os.environ.get("PORT", 5000))\
    app.run(host="0.0.0.0", port=port)\
}