from flask import Flask, render_template, request
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pyecharts import options as opts
from pyecharts.charts import Bar

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        df = pd.read_csv(filename)
        fig = px.scatter(df, x=df.columns[0], y=df.columns[1])
        plot_html = pio.to_html(fig, full_html=False)
        print(plot_html)
        return render_template('AI Fairness Dashboard.html', plot=plot_html)
    return render_template('AI Fairness Dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
