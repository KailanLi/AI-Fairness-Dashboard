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
# app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
df = None  # global variable to store the dataframe
grouped_df = None  # global variable to store the grouped dataframe
sensitive_attribute = None  # global variable to store the sensitive attribute
target_attribute = None  # global variable to store the target attribute

g10_colors = ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD',
              '#8C564B', '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF']

# Create a custom template
my_template = go.layout.Template()

# Update the default margin
my_template.layout.margin = dict(l=25, r=25, t=25, b=25)

# Update the default colorway
my_template.layout.colorway = g10_colors

# Set the default template
pio.templates['my_template'] = my_template
pio.templates.default = 'my_template'

@server.route('/', methods=['GET','POST'])
def upload_file():
    return render_template('AI Fairness Dashboard.html')

@server.route('/generate_visual', methods=['POST'])
def generate_visual():
    global df
    global sensitive_attribute
    global target_attribute
    global Prediction
    global grouped_df
    data = request.get_json()
    df = pd.DataFrame(data['transferredData'])
    sensitive_attribute = data['sensitiveAttribute']
    target_attribute = data['targetAttribute']
    Prediction = data['Prediction']
    print(Prediction)
    grouped_df = df.groupby([sensitive_attribute, target_attribute]).size().reset_index(name='counts')
    table_plot=generate_table()
    bar_plot=generate_bar()
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
    # bar_chart = px.histogram(grouped_df, x=sensitive_attribute, y='counts', color=target_attribute,title=sensitive_attribute )
    # fig = sp.make_subplots(rows=2, cols=2)
    # # Add the first trace from the bar chart to the subplot
    # for trace in bar_chart.data:
    #     fig.add_trace(trace, row=1, col=1)
    # fig.update_layout(barmode='stack')
    # bar_plot = pio.to_html(fig, full_html=False)
    sankey_chart = generate_sankey()
    sankey_plot = pio.to_html(sankey_chart, full_html=False)
    return jsonify({'table_plot':table_plot,'bar_plot': bar_plot, 'sankey_plot': sankey_plot})

def generate_bar():
    color_dict = {value: color for value, color in zip(df[target_attribute].unique(), px.colors.qualitative.G10)}
    fig = go.Figure()
    fig = sp.make_subplots(rows=1, cols=2,subplot_titles=(sensitive_attribute+" by "+target_attribute, sensitive_attribute+" by "+Prediction),shared_xaxes=False)
    # add traces for target attribute
    for value, color in color_dict.items():
        df_filtered = df[df[target_attribute] == value]
        fig.add_trace(
            go.Histogram(
                x=df_filtered[sensitive_attribute], 
                marker_color=color, 
                name=value
            ),
            row=1, col=1
        )
    # add traces for prediction
    for value, color in color_dict.items():
        df_filtered = df[df[Prediction] == value]
        fig.add_trace(
            go.Histogram(
                x=df_filtered[sensitive_attribute], 
                marker_color=color, 
                name=value
            ),
            row=1, col=2
        )    
    fig.update_layout(barmode='stack')
    bar = pio.to_html(fig, full_html=False)
    return bar



def generate_sankey():
    labels = list(df[sensitive_attribute].unique()) + list(df[target_attribute].unique())
    source = [labels.index(x) for x in grouped_df[sensitive_attribute]]
    target = [labels.index(x) for x in grouped_df[target_attribute]]
    value = grouped_df['counts'].tolist()
    # Define your nodes and links here
    nodes = dict(
        pad=15,
        thickness=20,
        line=dict(color=g10_colors, width=0.5),
        label=labels,
        color=g10_colors
    )

    link = dict(
        source=source, 
        target=target,
        value=value,
        color=g10_colors
        
    )

    data = go.Sankey(node=nodes, link=link,)

    sankey_chart = go.Figure(data)
    return sankey_chart

def generate_table():
    table = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='#1F77B4',
                    align='left'),
        cells=dict(values=[df[col] for col in df.columns],
                   fill_color='White',
                   align='left'))
    ])
    table_chart = pio.to_html(table, full_html=False)
    return table_chart

if __name__ == '__main__':
    server.run(debug=True)
