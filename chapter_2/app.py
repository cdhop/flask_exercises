from flask import Flask, request, make_response, redirect
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

@app.route('/user/<name>')
def user(name):
    return '<h1>Hello, ' + name + '!</h1>'

@app.route('/browser')
def browser():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is ' + user_agent + '</p>'

@app.route('/response')
def response():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response

@app.route('/redirect_example')
def redirect_example():
    return redirect('http://www.example.com')

if __name__ == '__main__':
    app.run(debug=True)
