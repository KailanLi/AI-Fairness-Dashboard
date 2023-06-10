from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pyecharts import options as opts
from pyecharts.charts import Bar

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
df = None  # global variable to store the dataframe

@app.route('/', methods=['GET','POST'])
def upload_file():
    return render_template('AI Fairness Dashboard.html')

@app.route('/generate_visual', methods=['POST'])
def generate_visual():
    global df
    data = request.get_json()
    df = pd.DataFrame(data['transferredData'])
    # print(df.head(1))
    sensitive_attribute = data['sensitiveAttribute']
    target_attribute = data['targetAttribute']
    print(sensitive_attribute)
    print(target_attribute)
    grouped_df = df.groupby([sensitive_attribute, target_attribute]).size().reset_index(name='counts')
    fig = px.bar(grouped_df, x=sensitive_attribute, y='counts', color=target_attribute)
    plotly_chart = pio.to_html(fig, full_html=False)
    return jsonify({'plot': plotly_chart})

    


if __name__ == '__main__':
    app.run(debug=True)
