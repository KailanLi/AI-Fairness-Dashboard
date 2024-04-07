from dash import Dash
import pandas as pd
import dash
from dash import dash_table,html
from dash import dcc, html, Input, Output
from flask import current_app as app,request
from .layout import html_layout
from flask import  session
from sklearn.metrics import confusion_matrix
# @app.route('/generate_visual', methods=['POST'])
# def getdata():
#     global alldf
#     data = request.get_json()
#     alldf = pd.DataFrame(data['transferredData'])
#     print(alldf.head(1))
#     return alldf

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/'
    )
    dash_app.index_string = html_layout
    
    # Initial layout with placeholders
    dash_app.layout = html.Div([
        dcc.Store(id='session-trigger', storage_type='session'),  # Trigger for our dynamic layout callback
        html.Div(id='dynamic-layout')  # Holds our dynamically generated content
    ])

    @dash_app.callback(
        Output('dynamic-layout', 'children'),
        [Input('session-trigger', 'data')]
    )
    def update_layout(_):
        # Retrieve data from session
        processed_data = session.get('processed_data')
        sensitive_attribute = session.get('sensitive_attribute')
        target_attribute = session.get('target_attribute')
        Prediction = session.get('Prediction')       

        # Based on the session data, generate and return the appropriate layout
        if processed_data:
            df = pd.DataFrame(processed_data)

            # Generate the main data table
            main_table = create_data_table(df)

            # Assume 'sensitive_attribute', 'target_attribute', and 'Prediction' are known and defined
            # Calculate fairness metrics
            fairness_metrics_df = calculate_fairness_metrics(df, sensitive_attribute, target_attribute, Prediction)

            # Generate the fairness metrics table
            fairness_metrics_table = create_fairness_metrics_table(fairness_metrics_df)

            return html.Div([
                html.Div(id='dash-container'),
                html.Div([
                    html.H3('Main Data Table'),
                    main_table,
                    html.H3('Fairness Metrics Table'),
                    fairness_metrics_table
                ])
            ])
        else:
            return html.Div([
                html.Div(id='dash-container'),
                "No data"
            ])

    return dash_app.server

def appdata():
    processed_data = session.get('processed_data')
    sensitive_attribute = session.get('sensitive_attribute')
    target_attribute = session.get('target_attribute')
    Prediction = session.get('Prediction')
    df=pd.DataFrame(processed_data)
    return df,sensitive_attribute,target_attribute,Prediction

def calculate_fairness_metrics(df, sensitive_attribute, target_attribute, prediction):
    """Calculate fairness metrics for binary text values in target and prediction."""
    metrics_df = pd.DataFrame(columns=['Group', 'Metric', 'Value'])

    # Define your positive and negative labels here
    positive_label = " >50K"  # or "Pass" or any other positive outcome representation
    negative_label = " <=50K"  # or "Fail" or any other negative outcome representation

    # Convert target and prediction to binary (0, 1) representation
    df[target_attribute] = df[target_attribute].apply(lambda x: 1 if x == positive_label else 0)
    df[prediction] = df[prediction].apply(lambda x: 1 if x == positive_label else 0)

    # Calculate metrics for each group
    for group in df[sensitive_attribute].unique():
        group_df = df[df[sensitive_attribute] == group]
        tn, fp, fn, tp = confusion_matrix(group_df[target_attribute], group_df[prediction]).ravel()

        # Statistical Parity (Demographic Parity)
        demographic_parity = group_df[prediction].mean()
        metrics_df = metrics_df.append({'Group': group, 'Metric': 'Demographic Parity', 'Value': demographic_parity}, ignore_index=True)

        # Equalized Odds components (True Positive Rate and False Positive Rate)
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Positive Rate
        metrics_df = metrics_df.append({'Group': group, 'Metric': 'True Positive Rate', 'Value': tpr}, ignore_index=True)
        metrics_df = metrics_df.append({'Group': group, 'Metric': 'False Positive Rate', 'Value': fpr}, ignore_index=True)

        # Predictive Parity (Positive Predictive Value)
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0  # Positive Predictive Value
        metrics_df = metrics_df.append({'Group': group, 'Metric': 'Positive Predictive Value', 'Value': ppv}, ignore_index=True)

    return metrics_df



def create_fairness_metrics_table(fairness_metrics_df, threshold=0.1):
    """Create Dash DataTable for fairness metrics with conditional formatting based on the specified threshold."""
    # Pivot the DataFrame and then round all numerical values to 2 decimal places
    pivoted_df = fairness_metrics_df.pivot(index='Group', columns='Metric', values='Value').reset_index().round(2)

    # Create columns for the Dash DataTable based on the pivoted and rounded DataFrame
    columns = [{"name": i, "id": i} for i in pivoted_df.columns]

    # Initialize the list for conditional styling
    style_data_conditional = []

    # Check differences between groups for each metric and add conditional formatting rules
    for metric in pivoted_df.columns[1:]:  # Skip the first column which is 'Group'
        max_value = pivoted_df[metric].max()
        min_value = pivoted_df[metric].min()
        
        # If the difference exceeds the threshold, highlight the metric name in red
        if (max_value - min_value) > threshold:
            style_data_conditional.append({
                'if': {'column_id': metric},
                'color': 'red'
            })

    table = dash_table.DataTable(
        id="fairness-metrics-table",
        columns=columns,
        data=pivoted_df.to_dict("records"),
        style_data_conditional=style_data_conditional,
        # Include any desired DataTable configurations
    )
    return table




def create_data_table(a):
    """Create Dash datatable from Pandas DataFrame."""
    table = dash_table.DataTable(
        id="table-container",
        columns=[{"name": i, "id": i} for i in a.columns],
        data=a.to_dict("records"),
        # Sorting
        sort_action="native",
        sort_mode="multi",
        # Column and row selection
        column_selectable="single",
        row_selectable="multi",
        # Pagination
        page_action="native",
        page_current=0,
        page_size=7,
        # Styling
        style_table={
            'overflowX': 'auto',
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        tooltip_data=[
            {
                column: {'value': str(row[column]), 'type': 'markdown'}
                for column in a.columns
            }
            for row in a.to_dict('records')
        ],
        tooltip_duration=None
    )
    return table




