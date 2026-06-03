from flask import Flask, render_template, request, session, redirect
import random

app = Flask(__name__)
app.secret_key = "secret123"


@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""

    if session.get('passed'):
        return render_template('index.html', passed=True)

    if 'num1' not in session:
        session['num1'] = random.randint(1, 10)
        session['num2'] = random.randint(1, 10)
        session['answer'] = session['num1'] + session['num2']

    if request.method == 'POST':
        user_answer = request.form.get('answer')

        if user_answer:
            if int(user_answer) == session['answer']:
                session.clear()
                session['passed'] = True
                return render_template('index.html', passed=True)
            else:
                result = "❌ Неверно, попробуйте ещё"

    return render_template(
        'index.html',
        num1=session.get('num1'),
        num2=session.get('num2'),
        result=result,
        passed=False
    )


@app.route('/reset')
def reset():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)