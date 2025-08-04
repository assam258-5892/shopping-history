from flask import Flask, redirect
from costco import costco_bp

app = Flask(__name__, static_folder='static', template_folder='templates')

# 여러 서비스 Blueprint 등록
app.register_blueprint(costco_bp)

# 메인 페이지 - 서비스 선택
@app.route('/')
def 홈():
    return redirect('/costco/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
