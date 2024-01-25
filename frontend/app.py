import dash
from dash import dcc, html
from frontend.callbacks.callbacks import create_app

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=5 * 60 * 1000),
    dcc.Store(id='user-session', storage_type='session'),
    dcc.Store(id='sign-in-session-update', storage_type='session'),
    dcc.Store(id='sign-up-session-update', storage_type='session'),
    html.Div(id='nav-bar'),
    html.Div(id='page-content', style={'backgroundColor': '#301934', 'width': '100%', 'height': '100vh', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center'})
])

if __name__ == '__main__':
    create_app(app)
    app.run(debug=True, host='0.0.0.0', port=9000)
