import os
import datetime
import sqlite3
from flask import Flask, render_template, g, url_for, redirect, request, flash, jsonify

app = Flask(__name__, static_folder='static', template_folder='templates')

class PrefixMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        return self.app(environ, start_response)

app.wsgi_app = PrefixMiddleware(app.wsgi_app)

@app.before_request
def safari_only():
    ua = request.headers.get('User-Agent', '')
    if not ('Safari' in ua and 'Chrome' not in ua and 'Chromium' not in ua):
        return '이 페이지는 현재 네트워크 환경에서 지원되지 않습니다. (ERR-42)', 403

데이터베이스 = os.path.join(os.path.dirname(__file__), 'instance', 'shopping.db')

def 데이터베이스_가져오기():
    디비 = getattr(g, '_database', None)
    if 디비 is None:
        디비 = g._database = sqlite3.connect(데이터베이스)
        디비.row_factory = sqlite3.Row
    return 디비

@app.teardown_appcontext
def 연결_닫기(예외):
    디비 = getattr(g, '_database', None)
    if 디비 is not None:
        디비.close()

@app.route('/')
def 루트():
    return redirect('/purchase')

# 날짜/매장 선택 페이지
@app.route('/purchase/select', methods=['GET'])
def 날짜_매장_선택():
    디비 = 데이터베이스_가져오기()
    매장목록 = 디비.execute('SELECT 번호, 매장명, 위도, 경도 FROM 매장 ORDER BY 번호').fetchall()
    오늘 = datetime.date.today().isoformat()
    return render_template('purchase/select.html', 매장목록=매장목록, 오늘=오늘)

@app.route('/purchase')
def 구매일자_목록():
    디비 = 데이터베이스_가져오기()
    구매목록들 = 디비.execute('''
        SELECT 구매일자, 매장명, 매장.번호 as 매장번호, SUM(구매금액) as 합계금액
          FROM 구매기록
          JOIN 매장 ON 구매기록.매장번호 = 매장.번호
         GROUP BY 구매일자, 매장명
         ORDER BY 구매일자 DESC, 매장명
    ''').fetchall()
    오늘 = datetime.date.today()
    일년전 = 오늘 - datetime.timedelta(days=365)
    합계 = 디비.execute(
        'SELECT SUM(구매금액) as 연간합계 FROM 구매기록 WHERE 구매일자 >= ? AND 구매일자 <= ?',
        (일년전.isoformat(), 오늘.isoformat())
    ).fetchone()
    if 합계 is None:
        합계 = {'연간합계': 0}
    return render_template('purchase/index.html', 구매목록들=구매목록들, 합계=합계)

@app.route('/purchase/list/<date>/<int:store_code>')
def 구매일자별_매장별_구매목록(date, store_code):
    구매목록 = 데이터베이스_가져오기().execute('''
        SELECT 일련번호, 품목명, 규격, 구매금액
          FROM 구매기록
          JOIN 품목 ON 품목코드 = 품목.코드
         WHERE 구매일자 = ? AND 매장번호 = ?
         ORDER BY 일련번호 DESC
    ''', (date, store_code)).fetchall()
    매장명 = 데이터베이스_가져오기().execute('SELECT 매장명 FROM 매장 WHERE 번호 = ?', (store_code,)).fetchone()
    매장명 = 매장명['매장명'] if 매장명 else ''
    return render_template('purchase/date.html', 구매일자=date, 매장명=매장명, 구매목록=구매목록, 매장번호=store_code)

# 품목 상세/수정/신규 페이지 (item_id==0: 신규)
@app.route('/purchase/item/<date>/<int:store_code>/<int:item_id>', methods=['GET', 'POST'])
def 품목_상세_수정(date, store_code, item_id):
    디비 = 데이터베이스_가져오기()
    if request.method == 'POST':
        if item_id != 0 and request.form.get('delete') == '1':
            디비.execute('DELETE FROM 구매기록 WHERE 일련번호 = ?', (item_id,))
            디비.commit()
            return redirect(url_for('구매일자별_매장별_구매목록', date=date, store_code=store_code))
        품목코드 = request.form.get('품목코드', '').strip()
        품목명 = request.form.get('품목명', '').strip()
        규격 = request.form.get('규격', '').strip()
        가격 = request.form.get('가격', '').replace(',', '').strip()
        할인금액 = request.form.get('할인금액', '').replace(',', '').strip()
        수량 = request.form.get('수량', '').replace(',', '').strip()
        구매금액 = request.form.get('구매금액', '').replace(',', '').strip()
        구매자번호 = request.form.get('구매자', '').strip()
        디비.execute('''
            INSERT INTO 품목 (코드, 품목명, 규격) VALUES (?, ?, ?) ON CONFLICT(코드) DO UPDATE SET 품목명=excluded.품목명, 규격=excluded.규격
        ''', (int(품목코드), 품목명, 규격))
        디비.commit()
        if 품목코드 and 품목명 and 구매금액.isdigit() and 가격.isdigit() and 할인금액.isdigit() and 수량.isdigit():
            if item_id == 0:
                디비.execute('''
                    INSERT INTO 구매기록 (구매일자, 매장번호, 품목코드, 가격, 할인금액, 수량, 구매금액, 구매자번호)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (date, store_code, int(품목코드), int(가격), int(할인금액), int(수량), int(구매금액), int(구매자번호) if 구매자번호 else None))
                디비.commit()
            else:
                디비.execute('''
                    UPDATE 구매기록 SET 품목코드 = ?, 가격 = ?, 할인금액 = ?, 수량 = ?, 구매금액 = ?, 구매자번호 = ? WHERE 일련번호 = ?
                ''', (int(품목코드), int(가격), int(할인금액), int(수량), int(구매금액), int(구매자번호) if 구매자번호 else None, item_id))
                디비.commit()
        return redirect(url_for('구매일자별_매장별_구매목록', date=date, store_code=store_code))
    if item_id == 0:
        매장 = 디비.execute('SELECT 매장명 FROM 매장 WHERE 번호 = ?', (store_code,)).fetchone()
        구매 = {
            '품목코드': '', '품목명': '', '규격': '', '가격': 0, '할인금액': 0, '수량': 1, '구매금액': 0, '구매자번호': 1,
            '구매일자': date, '매장번호': store_code, '매장명': 매장['매장명'] if 매장 else ''
        }
    else:
        구매 = 디비.execute('''
            SELECT 일련번호, 구매금액, 구매일자, 매장번호, 품목명, 품목.코드 as 품목코드, 규격, 수량, 가격, 할인금액, 매장명, 구매자명, 구매자번호
            FROM 구매기록
            JOIN 품목 ON 품목코드 = 품목.코드
            JOIN 매장 ON 매장번호 = 매장.번호
            LEFT JOIN 구매 ON 구매자번호 = 구매.번호
            WHERE 일련번호 = ?
        ''', (item_id,)).fetchone()
        if not 구매:
            return '존재하지 않는 품목입니다.', 404
    구매자목록 = 디비.execute('SELECT 번호, 구매자명 FROM 구매 ORDER BY 구매자명').fetchall()
    return render_template('purchase/item.html', 구매=구매, 구매자목록=구매자목록)

@app.route('/price')
def 가격정보():
    가격정보 = 데이터베이스_가져오기().execute('''
        SELECT 코드,
               품목명,
               규격,
               MAX(구매일자) as 최신구매일자,
               MAX(일련번호) as 최신일련번호,
               MIN(가격 - 할인금액) as 최소가격,
               MAX(가격 - 할인금액) as 최대가격
          FROM 품목
          LEFT JOIN 구매기록 ON 품목코드 = 코드
         GROUP BY 코드, 품목명, 규격
         ORDER BY 최신구매일자 DESC NULLS LAST, 최신일련번호 DESC NULLS LAST, 품목명
    ''').fetchall()
    return render_template('price/index.html', 가격정보=가격정보)

@app.route('/price/<int:item_code>')
def 가격정보_상세(item_code):
    디비 = 데이터베이스_가져오기()
    기록 = 디비.execute('''
        SELECT 구매일자, 매장명, 가격 - 할인금액 AS 최종가격
          FROM 구매기록
          JOIN 품목 ON 품목코드 = 코드
          JOIN 매장 ON 매장번호 = 번호
         WHERE 코드 = ?
         ORDER BY 구매일자 DESC, 일련번호 DESC
    ''', (item_code,)).fetchall()
    품목 = 디비.execute('SELECT 품목명, 규격 FROM 품목 WHERE 코드 = ?', (item_code,)).fetchone()
    return render_template('price/detail.html', 품목=품목, 기록=기록)

@app.route('/api/item-name/<int:code>')
def 품목정보_API(code):
    디비 = 데이터베이스_가져오기()
    품목 = 디비.execute('SELECT 품목명, 규격 FROM 품목 WHERE 코드 = ?', (code,)).fetchone()
    가격 = 디비.execute('SELECT 가격 FROM 구매기록 WHERE 품목코드 = ? ORDER BY 구매일자 DESC, 일련번호 DESC LIMIT 1', (str(code),)).fetchone()
    return jsonify({'품목명': 품목['품목명'] if 품목 else None, '규격': 품목['규격'] if 품목 else None, '가격': 가격['가격'] if 가격 else None})

if __name__ == '__main__':
    app.run(debug=True)
