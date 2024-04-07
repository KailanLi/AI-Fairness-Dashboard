html_layout = """
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body class="dash-template">
            <header>
              <div class="nav-wrapper">
                <nav>
                </nav>
            </div>
            </header>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
"""

graph_html_layout = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Fairness Dashboard</title>
    <!-- <link rel="icon" type="image/png" href="UTS ICON.png"> -->
    <link rel="stylesheet" href="{{ url_for('static', filename='UTS ICON.png') }}">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <script src="https://d3js.org/d3.v5.min.js"></script>
    <link rel="stylesheet" href="/static/style.css">
    <script src="{{ url_for('application/static', filename='script.js') }}"></script>
</head>
<body>
    <div class="container-fluid">
        <!-- Header section -->
        <div class="row">
            <div class="col-md-12">
                <h1>AI Fairness Dashboard</h1>
            </div>
            <div class="navbar">
                <a href="/">Reload Data</a>
                <a href="/dashapp">Show Table and Visuals</a>
                <a href="/graphapp">Show Casual</a>
                <!-- You can add more links here in the future -->
            </div>
        </div>
        <div class="row">
            <!-- Visualization and data table section -->
            <div class="col-md-12">
                {%app_entry%} <!-- Dash app content will be rendered here -->
            </div>
        </div>
    </div>
    {%config%}
    {%scripts%}
    {%renderer%}
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://unpkg.com/d3@5.9.7"></script>
    <script src="https://unpkg.com/d3-sankey@0.12.3"></script>
    <script src="https://d3js.org/d3-scale-chromatic.v1.min.js"></script>
</body>
</html>
"""
