from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('AI Fairness Dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
