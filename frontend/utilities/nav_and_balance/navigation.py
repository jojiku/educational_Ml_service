from dash import dcc, html

def navigation_bar(user_session):
    if user_session and user_session.get('is_authenticated'):
        return html.Div([
            dcc.Link('Billing', href='/billing', style={
                'backgroundColor': '#00FFFF',
                'color': 'black',
                'textDecoration': 'none',
                'padding': '5px 15px',
                'fontWeight': '500',
                'display': 'inline-block',
                'transition': 'color 0.3s',
                'textAlign': 'right'}),

            dcc.Link('Prediction', href='/prediction', style={
                'backgroundColor': '#00FFFF',
                'color': 'black', 
                'padding': '5px 15px',
                'fontWeight': '500',
                'transition': 'color 0.3s',
                'textAlign': 'left'})], 

            style={
                'padding': '20px 15px',
                'fontSize': '18px',
                'textAlign': 'center',
                'fontWeight': 'bold',
                'backgroundcolor': 'cyan'
})
