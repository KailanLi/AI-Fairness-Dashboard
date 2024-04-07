from dash import Dash, dcc, html, Input, Output, dash_table, dependencies
import plotly.graph_objects as go
import networkx as nx
from flask import current_app as app, request, session
from dash import callback_context
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from .layout import graph_html_layout

def init_graph_app(server):
    graph_app = Dash(
        server=server,
        routes_pathname_prefix='/graphapp/'
    )
    graph_app.index_string = graph_html_layout

    nodes = ["age", "edunum", "maritalstatus", "relationship", "race", "sex",
             "capitalgain", "hoursperweek", "country", "income", "occupation"]

    edges = [
        ("age", "capitalgain"),
        ("age", "income"),
        ("edunum", "income"),
        ("race", "edunum"),
        ("race", "occupation"),
        ("sex", "relationship"),
        ("sex", "hoursperweek"),
        ("sex", "occupation"),
        ("capitalgain", "maritalstatus"),
        ("capitalgain", "hoursperweek"),
        ("capitalgain", "income"),
        ("hoursperweek", "country"),
        ("hoursperweek", "income"),
        ("country", "relationship"),
        ("country", "race")
    ]

    G = nx.DiGraph()
    import random
    G.add_nodes_from(nodes)
    for edge in edges:
        G.add_edge(edge[0], edge[1], weight=random.random())

    graph_app.layout = html.Div([
            dcc.Graph(id='graph'),
            html.Label('Select Source Node:'),
            dcc.Dropdown(
                id='source-node-dropdown',
                options=[{'label': node, 'value': node} for node in G.nodes()],
                value=list(G.nodes())[0] if G.nodes() else None
            ),
            html.Label('Select Target Node:'),
            dcc.Dropdown(
                id='target-node-dropdown',
                options=[{'label': node, 'value': node} for node in G.nodes()],
                value=list(G.nodes())[1] if len(G.nodes()) > 1 else None
            ),
            html.Button('Add Edge', id='add-edge-button'),
            html.Button('Remove Edge', id='remove-edge-button'),
            html.Div(id='all-paths', children='')  # This is the new Div element
        ])

    def cubic_bezier(t, start, ctrl, end):
        return (
            (1 - t) ** 2 * start + 2 * (1 - t) * t * ctrl + t ** 2 * end
        )

    @graph_app.callback(
        [Output('graph', 'figure'), Output('all-paths', 'children')],
        [Input('add-edge-button', 'n_clicks'),
        Input('remove-edge-button', 'n_clicks'), 
        Input('graph', 'clickData'),
        Input('source-node-dropdown', 'value'),
        Input('target-node-dropdown', 'value')]
    )



    def update_graph(add_clicks, remove_clicks, clickData, source_node, target_node):
        ctx = callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "add-edge-button":
            G.add_edge(source_node, target_node, weight=1)
        elif button_id == "remove-edge-button" and G.has_edge(source_node, target_node):
            G.remove_edge(source_node, target_node)

        pos = nx.spring_layout(G)

        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]

        edge_weights = np.array([G[edge[0]][edge[1]]['weight'] for edge in G.edges()])
        normalized_weights = (edge_weights - edge_weights.min()) / (edge_weights.max() - edge_weights.min() + 1e-10)
        
        colormap = plt.get_cmap('magma_r')
        edge_colors = [mcolors.rgb2hex(colormap(weight)) for weight in normalized_weights]

        

        node_adjacencies = []
        node_text = []
        for node, adjacencies in enumerate(G.adjacency()):
            node_adjacencies.append(len(adjacencies[1]))
            node_text.append(adjacencies[0])
        
        
# Create a mapping of nodes to their individual source and target nodes
        node_adjacencies = {}
        for node in G.nodes():
            source_nodes = list(G.predecessors(node))
            target_nodes = list(G.successors(node))
            hover_text_list = [f"{src} -> {node}" for src in source_nodes] + [f"{node} -> {tgt}" for tgt in target_nodes]
            hover_text = '<br>'.join(hover_text_list)  # Use HTML line break for multiline hover text
            node_adjacencies[node] = hover_text

        # Update hovertext in node_trace
        hovertext=[node_adjacencies.get(node, '') for node in G.nodes()],

        node_trace = go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers+text',
                    hoverinfo='text',
                    hovertext=[node_adjacencies[node] for node in G.nodes()],
                    text=node_text,
                    textposition='top center',
                    marker=dict(
                        color='#787276',
                        size=50,
                        line_width=2
                    )
                )


        edge_traces = []
        for i, edge in enumerate(G.edges()):
            x0, y0 = pos.get(edge[0], (None, None))
            x1, y1 = pos.get(edge[1], (None, None))

            if None in [x0, y0, x1, y1]:
                continue

            # Calculate control points for cubic Bezier curve
            ctrl_x, ctrl_y = (x0 + x1) / 2, (y0 + y1) / 2
            ctrl_x += 0.2 * (y1 - y0)
            ctrl_y -= 0.2 * (x1 - x0)

            stop_t = 0.98  # Where to stop the curve
            bezier_x = [cubic_bezier(t, x0, ctrl_x, x1) for t in np.linspace(0, stop_t, 30)]
            bezier_y = [cubic_bezier(t, y0, ctrl_y, y1) for t in np.linspace(0, stop_t, 30)]

            
            
            # # Calculate the arrow direction
            # dx = bezier_x[-1] - bezier_x[-2]
            # dy = bezier_y[-1] - bezier_y[-2]
            
            # # Normalize the arrow direction
            # length = np.sqrt(dx ** 2 + dy ** 2)
            # dx /= length
            # dy /= length

            # # Explicit arrow size
            # arrow_length = 0.02  # Fixed length
            # arrow_width = 0.01  # Fixed width
            
            # # Calculate arrowhead points
            # arrow_x1 = bezier_x[-1] - arrow_length * dx + arrow_width * dy
            # arrow_y1 = bezier_y[-1] - arrow_length * dy - arrow_width * dx
            # arrow_x2 = bezier_x[-1] - arrow_length * dx - arrow_width * dy
            # arrow_y2 = bezier_y[-1] - arrow_length * dy + arrow_width * dx
            
            # # Create the arrow trace
            # arrow_trace = go.Scatter(
            #     x=[arrow_x1, bezier_x[-1], arrow_x2, None],
            #     y=[arrow_y1, bezier_y[-1], arrow_y2, None],
            #     line=dict(width=2, color=edge_colors[i]),
            #     hoverinfo='none',
            #     mode='lines'
            # )


            
            edge_trace = go.Scatter(
                x=bezier_x,
                y=bezier_y,
                line=dict(width=2, color=edge_colors[i]),
                hoverinfo='none',
                mode='lines'
            )
            
            edge_traces.extend([edge_trace])



        layout = go.Layout(
            title='Fairness Graph',
            titlefont_size=16,
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )

        dummy_trace = go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(
                colorscale="magma_r",
                cmin=min(edge_weights),
                cmax=max(edge_weights),
                colorbar=dict(
                    title="Edge Weights"
                ),
                color=[]
            )
        )

        
# Inside update_graph callback
        # Debugging added to original code snippet
# Debugging added to the original code snippet
        dimmed_edge_colors = edge_colors.copy()
        node_colors = ['#D3D3D3'] * len(G.nodes())

        if callback_context.inputs.get('graph.clickData') is not None:
            print("Inside clickData condition.")  # Debug
            
            clickData = callback_context.inputs['graph.clickData']

            # Check if 'text' key exists in clickData
            if 'text' in clickData['points'][0]:
                clicked_node = clickData['points'][0]['text']
                
                source_nodes = list(G.predecessors(clicked_node))
                target_nodes = list(G.successors(clicked_node))

                # Dim all nodes to light gray first
                node_colors = ['#D3D3D3'] * len(G.nodes())
                
                # Highlight clicked node with Orange-red color
                node_colors[list(G.nodes()).index(clicked_node)] = '#FF4500'  # Orange-red for clicked node

                # Highlight connected nodes with Yellow color
                for node in source_nodes + target_nodes:
                    node_colors[list(G.nodes()).index(node)] = '#FFFF00'

                # Dim the edges that are not connected to the clicked node
                for i, (src, tgt) in enumerate(G.edges()):
                    if not (src == clicked_node or tgt == clicked_node):
                        dimmed_edge_colors[i] = '#D3D3D3'  # Dim to light gray

                print("Updated node_colors:", node_colors)  # Debug
                print("Updated edge_colors:", dimmed_edge_colors)  # Debug

        # Update the node and edge colors before constructing the figure
        node_trace.marker.color = node_colors
        for i, edge_trace in enumerate(edge_traces):
            edge_trace.line.color = dimmed_edge_colors[i]


        

        # Construct the figure
        fig = go.Figure(data=[*edge_traces, dummy_trace, node_trace], layout=layout)


        

        all_paths_text = ''
        if source_node and target_node:
            try:
                all_paths = list(nx.all_simple_paths(G, source=source_node, target=target_node))
                all_paths_text = 'All paths from {} to {}: {}'.format(source_node, target_node, all_paths)
            except nx.NetworkXNoPath:
                all_paths_text = 'No path from {} to {}'.format(source_node, target_node)
        
        return fig, all_paths_text
        

    return graph_app.server
