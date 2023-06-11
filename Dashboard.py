from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pyecharts import options as opts
from pyecharts.charts import Bar
import plotly.subplots as sp
import plotly.graph_objs as go
import dash
from dash import dash_table,html

server = Flask(__name__)
server.config['UPLOAD_FOLDER'] = 'static/uploads/'
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
df = pd.DataFrame()  # global variable to store the dataframe
grouped_df = None  # global variable to store the grouped dataframe
sensitive_attribute = None  # global variable to store the sensitive attribute
target_attribute = None  # global variable to store the target attribute

@server.route('/', methods=['GET','POST'])
def upload_file():
    return render_template('AI Fairness Dashboard.html')

@server.route('/generate_visual', methods=['POST'])
def generate_visual():
    global df
    global sensitive_attribute
    global target_attribute
    global grouped_df
    data = request.get_json()
    df = pd.DataFrame(data['transferredData'])
    sensitive_attribute = data['sensitiveAttribute']
    target_attribute = data['targetAttribute']
    print(sensitive_attribute)
    grouped_df = df.groupby([sensitive_attribute, target_attribute]).size().reset_index(name='counts')
    table_plot=generate_table()
    # app.layout = html.Div([   老晁，这段跑不出来，我现在可以实现简单的打印整表，这段代码可以分表，但是用的
    # dash_table.DataTable(     dash的一个库，和flask是矛盾的，所以实现起来很复杂
    #     id='table-paging',
    #     columns=[{"name": i, "id": i} for i in df.columns],
    #     data=df.to_dict('records'),
    #     page_current=0,
    #     page_size=10,
    #     page_action='custom'
    #     )
    # ])
    bar_chart = px.bar(grouped_df, x=sensitive_attribute, y='counts', color=target_attribute)
    fig = sp.make_subplots(rows=2, cols=2)
    # Add the first trace from the bar chart to the subplot
    for trace in bar_chart.data:
        fig.add_trace(trace, row=1, col=1)
    fig.update_layout(barmode='stack')
    bar_plot = pio.to_html(fig, full_html=False)
    sankey_chart = generate_sankey()
    sankey_plot = pio.to_html(sankey_chart, full_html=False)
    return jsonify({'table_plot':table_plot,'bar_plot': bar_plot, 'sankey_plot': sankey_plot})

def generate_sankey():
    global grouped_df
    global sensitive_attribute
    global target_attribute
    labels = list(df[sensitive_attribute].unique()) + list(df[target_attribute].unique())
    source = [labels.index(x) for x in grouped_df[sensitive_attribute]]
    target = [labels.index(x) for x in grouped_df[target_attribute]]
    value = grouped_df['counts'].tolist()
    # Define your nodes and links here
    nodes = dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color="blue"
    )

    link = dict(
        source=source, 
        target=target,
        value=value
    )

    data = go.Sankey(node=nodes, link=link,)

    sankey_chart = go.Figure(data)
    return sankey_chart

def generate_table():
    table = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='lavender',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='grey',
                   align='left'))
    ])
    table_chart = pio.to_html(table, full_html=False)
    return table_chart

if __name__ == '__main__':
    server.run(debug=True)
