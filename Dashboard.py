from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pyecharts import options as opts
from pyecharts.charts import Bar
import plotly.subplots as sp
import plotly.graph_objs as go
import matplotlib.colors as mcolors
import plotly.figure_factory as ff
from sklearn.metrics import confusion_matrix
import dash
from dash import dash_table,html

server = Flask(__name__)
server.config['UPLOAD_FOLDER'] = 'static/uploads/'
# app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
df = None  # global variable to store the dataframe
grouped_df = None  # global variable to store the grouped dataframe
sensitive_attribute = None  # global variable to store the sensitive attribute
target_attribute = None  # global variable to store the target attribute


# Create a custom template
my_template = go.layout.Template()

# Update the default margin
my_template.layout.margin = dict(l=30, r=30, t=30, b=30)

# Update the default colorway
my_template.layout.colorway = px.colors.qualitative.G10

# Set the default template
pio.templates['my_template'] = my_template
pio.templates.default = 'my_template'

@server.route('/', methods=['GET','POST'])
def Homepage():
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
    df_prediction_modified = df.copy()
    df_prediction_modified[Prediction] = "Predicted" + df_prediction_modified[Prediction].astype(str)
    # get the unique labels for each attribute
    labels = list(df[target_attribute].unique()) + list(df[sensitive_attribute].unique()) + list(df_prediction_modified[Prediction].unique())
    colorPalette = px.colors.qualitative.G10

    # Assign colors to nodes for target_attribute and Prediction
    colorDict = {}
    usedColors = []
    for i, label in enumerate(df[target_attribute].unique()):
        color = colorPalette[i % len(colorPalette)]   # Cycling through G10 colors if there are more than 10 unique values
        colorDict[label] = color
        usedColors.append(color)

    for i, label in enumerate(df_prediction_modified[Prediction].unique()):
        color = colorPalette[i % len(colorPalette)]   # Cycling through G10 colors if there are more than 10 unique values
        colorDict[label] = color
        usedColors.append(color)

    # Assign different colors to nodes for sensitive_attribute
    for i, label in enumerate(df[sensitive_attribute].unique()):
        color = colorPalette[(i+len(df[target_attribute].unique())+len(df_prediction_modified[Prediction].unique())) % len(colorPalette)]   # Cycling through G10 colors if there are more than 10 unique values
        if color not in usedColors:   # Check if the color has already been used
            colorDict[label] = color
        else:   # If the color has been used, find a new color
            for newColor in colorPalette:
                if newColor not in usedColors:
                    colorDict[label] = newColor
                    usedColors.append(newColor)
                    break

    # get the counts for the flow from target_attribute to sensitive_attribute
    target_to_sensitive = df.groupby([target_attribute, sensitive_attribute]).size().reset_index(name='counts')
    source_ts = [labels.index(x) for x in target_to_sensitive[target_attribute]]
    target_ts = [labels.index(x) for x in target_to_sensitive[sensitive_attribute]]
    value_ts = target_to_sensitive['counts'].tolist()

    # get the counts for the flow from sensitive_attribute to Prediction
    sensitive_to_prediction = df_prediction_modified.groupby([sensitive_attribute, Prediction]).size().reset_index(name='counts')
    source_sp = [labels.index(x) for x in sensitive_to_prediction[sensitive_attribute]]
    target_sp = [labels.index(x) for x in sensitive_to_prediction[Prediction]]
    value_sp = sensitive_to_prediction['counts'].tolist()

    # define the nodes and links for the Sankey diagram
    nodes = dict(
        pad=35,
        thickness=13,
        line=dict(color=colorPalette, width=0.5),
        label=labels,
        color=[colorDict[label] for label in labels]
    )
    def hex_to_rgba(hex_color, opacity=1):
        rgb = mcolors.hex2color(hex_color)
        return 'rgba' + str(rgb + (opacity,))
    
    link = dict(
        source=source_ts + source_sp, 
        target=target_ts + target_sp,
        value=value_ts + value_sp,
       color=[hex_to_rgba(colorDict[labels[src]], opacity=0.2) for src in source_ts + source_sp]   # Set all link colors to match with the colors each node in sensitive_attribute used but with 0.2 opacity
    )

    data = go.Sankey(node=nodes, link=link)
    sankey_chart = go.Figure(data)
    return sankey_chart


def generate_table():
    # Compute the maximum length of each column
    column_widths = [max([len(str(x)) for x in df[col].values] + [len(col)]) * 8 for col in df.columns]

    table = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>{}</b>'.format(col) for col in df.columns],  # Make column names bold
            fill_color=px.colors.qualitative.G10[0],
            align='center',
            font=dict(color='white', size=12, family="Arial, monospace"),
            height=40,
        ),
        cells=dict(
            values=[df.head(20)[col] for col in df.columns],
            fill_color='white',
            align='center',
            font=dict(size=12, family="Arial, monospace"),
            height=30,
        ),
        columnwidth=30,  # Set column widths
        )]
    )

    # Configure table
    for i in range(len(table.layout.annotations)):
        table.layout.annotations[i].align = "center"

    table.update_layout(
        autosize=True,
    )

    table_chart = pio.to_html(table, full_html=False)

    return table_chart



def generate_confusion_matrix(df, target_attribute, prediction):
    # Compute confusion matrix
    cm = confusion_matrix(df[target_attribute], df[prediction])

    # Convert confusion matrix to z-scores for heatmap
    z = cm[::-1]

    # Change each element of z to type string for annotations
    z_text = [[str(y) for y in x] for x in z]

    # Set up the figure 
    fig = ff.create_annotated_heatmap(z, annotation_text=z_text, colorscale='Viridis')

    # Add title
    fig.update_layout(title_text='<i><b>Confusion matrix</b></i>',
                      # Add x-axis and y-axis labels
                      xaxis = dict(title='Predicted value',
                                   tickmode='array',
                                   tickvals=[0,1],
                                   ticktext=['Negative', 'Positive']),
                      yaxis = dict(title='Actual value',
                                   tickmode='array',
                                   tickvals=[0,1],
                                   ticktext=['Positive', 'Negative'],
                                   autorange="reversed"),
                      # Add colorbar
                      autosize=True)

    return fig

@server.route('/Confusion Matrix')   
def generate_confusion_matrix_route():
    target_attribute = df[sensitive_attribute]
    Prediction = df[Prediction]
    fig = generate_confusion_matrix(df, target_attribute, Prediction)
    confusion_matrix_plot = pio.to_html(fig, full_html=False)
    return jsonify({'confusion_matrix_plot': confusion_matrix_plot})


if __name__ == '__main__':
    server.run(debug=True)
