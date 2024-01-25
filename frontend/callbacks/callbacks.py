import json
from datetime import datetime
from json import JSONDecodeError
from dash import dcc, html, dash_table
from dash import Output, Input, State, callback_context, ALL, dcc
from dash.exceptions import PreventUpdate

from frontend.data.local_data import authentificated_session
from frontend.data.remote_data import deposit_amount, send_prediction_request, \
    fetch_prediction_history, register_user, fetch_models, authenticate_user, fetch_user_balance
from frontend.utilities.nav_and_balance.navigation import navigation_bar

sign_page_last_click_timestamp = datetime.now()  

def estimated_cost(total_cost):
                    return html.Div(f"It'll cost you {total_cost} credits", style={'color': '#00FFFF', 'fontSize': '20px',
                    'fontSize': '16px',
                    'lineHeight': '1.6',
                    'fontFamily': '"Comfortaa", sans-serif',
                })

def prediction_history_table(predictions):
                    batches = {}
                    for prediction in predictions:
                        batch_key = (prediction["model_name"], prediction["timestamp"], prediction["cost"], prediction["id"])
                        if batch_key not in batches:
                            batches[batch_key] = []
                        batches[batch_key].extend(prediction.get('predictions', []))

                    batch_tables = []
                    for (model_name, timestamp, cost, _), preds in batches.items():
                        data = [
                            {
                             "predicted_category_label": pred["target"]["category_label"], 
                            }
                            for pred in preds
                        ]
                        columns = [
                            {"name": "Predicted Category Label", "id": "predicted_category_label"}]

                        batch_info = html.Div([
                            dash_table.DataTable(
                                columns=columns,
                                data=data)
                        ])
                    
                        batch_tables.append(batch_info)

                    return html.Div(batch_tables)


def create_app(_app):
    @_app.callback(
        Output('user-session', 'data'),
        [
            Input('sign-in-session-update', 'data'),
            Input('sign-up-session-update', 'data'),
        ],
        State('user-session', 'data')
    )
    def manage_session(sign_in_data, sign_up_data,
                       current_session):
        ctx = callback_context

        if not ctx.triggered:
            return current_session
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'sign-in-session-update' and sign_in_data:
            return sign_in_data
        elif trigger_id == 'sign-up-session-update' and sign_up_data:
            return sign_up_data

        return current_session

    @_app.callback(
        Output('url', 'pathname'),
        [Input({'type': 'nav-button', 'index': ALL}, 'n_clicks_timestamp'),
         Input('user-session', 'data')],
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def manage_navigation(n_clicks_timestamp, user_session, pathname):
        global sign_page_last_click_timestamp
        ctx = callback_context

        if user_session and user_session.get('is_authenticated', False) and pathname in ['/sign-in', '/sign-up']:
            return '/prediction'
        else:
            if not ctx.triggered:
                raise PreventUpdate

            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if not button_id:
                raise PreventUpdate

            try:
                button_index = json.loads(button_id.replace('\'', '"'))['index']
            except JSONDecodeError:
                raise PreventUpdate

            click_timestamp = max(n_clicks_timestamp) if n_clicks_timestamp else None

            if click_timestamp and (datetime.now() - sign_page_last_click_timestamp).total_seconds() > 1:
                sign_page_last_click_timestamp = datetime.now()
                if button_index == 'sign-up':
                    return '/sign-up'
                elif button_index == 'sign-in':
                    return '/sign-in'
            else:
                raise PreventUpdate

    @_app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')],
        [State('user-session', 'data')]
    )
    def manage_page_content(pathname, user_session):
        if user_session and user_session.get('is_authenticated'):
            # Prediction page
            if pathname == '/prediction':
                def create_merchant_cluster_pair(index):
                    return html.Div([
                        html.Div([
                            dcc.Input(
                                id={'type': 'input-cluster', 'index': index},
                                type='number',
                                placeholder='What is your sex? 1 - Male, 2 - Female',
                                style={'width': '400px', 'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px'}
                            )
                        ], style={'marginBottom': '10px'}), 

                        html.Div([
                            dcc.Input(
                                id={'type': 'input-merchant', 'index': index},
                                type='number',
                                placeholder='Years of work activity?',
                                style={'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px', 'marginRight': '10px'}
                            ),

                            dcc.Input(
                                id={'type': 'input-cluster', 'index': index},
                                type='number',
                                placeholder='body mass index',
                                style={'width': '260px', 'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px'}
                            )
                        ], style={'marginBottom': '10px'}), 

                        html.Div([
                            html.H2('Do you have diabetes?', style={'color': '#00FFFF', 'backgroundColor': '#192b34',
                                                                                                'alignItems': 'center', 'justifyContent': 'center'}), 
                            dcc.Input(
                            id={'type': 'input-merchant', 'index': index},
                            type='number',
                            placeholder='1 - Yes, 2 - No, 3 - Borderline',
                            style={'width': '600px', 'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px', 'marginRight': '10px', 'alignment':'center', 'alignItems': 'center', 'justifyContent': 'center'}
                            )]), 

                        html.Div([
                            dcc.Input(
                                id={'type': 'input-merchant', 'index': index},
                                type='number',
                                placeholder='Fasting Glucose',
                                style={'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px', 'marginRight': '10px'}
                            ),

                            dcc.Input(
                                id={'type': 'input-merchant', 'index': index},
                                type='number',
                                placeholder='Two Hour Glucose',
                                style={'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px', 'marginRight': '10px'}
                            ),

                            dcc.Input(
                            id={'type': 'input-merchant', 'index': index},
                            type='number',
                            placeholder='Insuline level',
                            style={'padding': '12px', 'borderRadius': '8px', 'outline': 'none', 'boxSizing': 'border-box', 'fontSize': '16px', 'marginRight': '10px', 'alignment':'center', 'alignItems': 'center', 'justifyContent': 'center'}
                            )])
                    ])
                def prediction_form():
                    return html.Div([
                        html.Div([dcc.Dropdown(
                            id='model-dropdown',
                            options=[],
                            placeholder='Choose a model here',
                            style={
                                'fontSize': '16px',
                                'marginBottom': '20px',
                                'width': '200px'
                            }
                        )]),
                        html.Div([html.Div(id='merchant-cluster-pairs', children=[create_merchant_cluster_pair(0)]),
                        html.Div(
                            html.Div(estimated_cost(None), id='estimated-cost'), style={'marginBottom': '40px'}),
                        html.Div([
                        html.Button('Predict', id='predict-button', n_clicks=0, style={
                            'backgroundColor': '#00FFFF',
                            'color': '#301934',
                            'padding': '12px 18px',
                            'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.12)'
                        })])])
                    ], style={'display': 'flex', 'justifyContent': 'flex-start', 'marginBottom': '20px'})

            
                balance = fetch_user_balance(user_session)
                predictions = fetch_prediction_history(user_session)
    
                return html.Div([html.Div(html.H3(f"Balance: {balance}"), id='current-balance-predictions'),
                                 prediction_form(),
                                 html.Div(prediction_history_table(predictions), id='prediction-history-table')])
            
            # Billing page
            elif pathname == '/billing':
                def deposit_form():
                    return html.Div([
                        html.Div([
                            dcc.Input(
                                id="deposit-amount",
                                placeholder="How many credits are needed?",type="number",
                                value="",
                                style={'color': '#00FFFF', 
                                    'width': '600px',
                                    'padding': '12px',
                                    'backgroundColor': '#301934', 
                                    'fontSize': '40px'}
                            ),
                        ]),
                        html.Div([
                            html.Button(
                                "Get credits",
                                id="deposit-button",
                                n_clicks=0,
                                style={'backgroundColor': '#00FFFF', 
                                    'padding': '12px 18px', 'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.12)'}
                            ),
                        ]),
                    ], style={'alignItems': 'center'})
                balance = fetch_user_balance(user_session)
                return html.Div([deposit_form(), html.H2('Your new balance is:', id='current-balance-text', style={'color': '#00FFFF', 'fontFamily': 'Comfortaa'}),
                                 html.Div(html.H3(f"Balance: {balance}"), id='current-balance-billing'),],
                                 style={'backgroundColor': '#301934', 'width': '100%', 'height': '100vh', 'display': 'flex', 
                                        'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'})
            
            
            else:
                return "404 Page Not Found"
        else:
            if pathname == '/sign-in':
                return html.Div([
                    html.H2("Sign In", style= {'color': '#00FFFF', 'fontFamily': 'Comfortaa'}),
                    html.Div([
                    dcc.Input(id="sign-in-email", type="email", placeholder="Email", autoFocus=True, style={'marginBottom': '15px', 'width': '100%'}),
                    dcc.Input(id="sign-in-password", type="password", placeholder="Password", style={'marginBottom': '15px', 'width': '100%'}),
                    html.Div([
                        html.Button("Sign In", id={'type': 'auth-button', 'action': 'sign-in'}, n_clicks=0,
                                    style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'}),
                        html.Button("Click here to sign up", id={'type': 'nav-button', 'index': 'sign-up'}, n_clicks=0,
                                    style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'})
                    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
                ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),
                    html.Div(id="sign-in-status", style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'})
                ], style={'maxWidth': '100px', 'margin': '0 auto', 'padding': '20px'})
            
            elif pathname == '/sign-up':
                    return html.Div([
                        html.H2("Sign Up", style= {'color': '#00FFFF', 'fontFamily': 'Comfortaa'}),
                        html.Div([
                        dcc.Input(id="sign-up-name", type="text", placeholder="Hi! What's your name?", style={'marginBottom': '15px', 'width': '100%'}),
                        dcc.Input(id="sign-up-email", type="email", placeholder="Your email please", autoFocus=True, style={'marginBottom': '15px', 'width': '100%'}),
                        dcc.Input(id="sign-up-password", type="password", placeholder="And password", style={'marginBottom': '15px', 'width': '100%'}),
                        html.Div([
                            html.Button("Sign Up", id={'type': 'auth-button', 'action': 'sign-up'}, n_clicks=0,
                                        style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'}),
                            html.Button("Click here to sign In", id={'type': 'nav-button', 'index': 'sign-in'}, n_clicks=0,
                                        style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'})
                        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
                    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),
                        html.Div(id="sign-up-status", style= {'backgroundColor': '#121212', 'color': '#00FFFF', 'fontFamily': 'Comfortaa'})
                    ], style={'maxWidth': '200px', 'margin': '0 auto', 'padding': '20px'})
            else:
                return dcc.Location(id='url', href='/sign-in', refresh=True)
    @_app.callback(
        Output('nav-bar', 'children'),
        [Input('user-session', 'data')]
    )
    def manage_navigation_bar(user_session):
        if user_session and user_session.get('is_authenticated'):
            return navigation_bar(user_session)
        return ""

    @_app.callback(
        [
            Output('sign-in-session-update', 'data'),
            Output('sign-in-status', 'children'),
        ],
        [
            Input({'type': 'auth-button', 'action': 'sign-in'}, 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('sign-in-email', 'value'),
            State('sign-in-password', 'value'),
        ],
        prevent_initial_call=True
    )



    def sign_in_callback(sign_in_clicks, _, sign_in_email, sign_in_password):
        if sign_in_clicks > 0:
            user_data, error = authenticate_user(sign_in_email, sign_in_password)
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Sign in successful"
            return None
        raise PreventUpdate

    @_app.callback(
        [
            Output('sign-up-session-update', 'data'),
            Output('sign-up-status', 'children'),
        ],
        [
            Input({'type': 'auth-button', 'action': 'sign-up'}, 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('sign-up-email', 'value'),
            State('sign-up-password', 'value'),
            State('sign-up-name', 'value'),
        ],
        prevent_initial_call=True
    )
    def sign_up_callback(sign_up_clicks, _, sign_up_email, sign_up_password, sign_up_name):
        if sign_up_clicks > 0:
            user_data, error = register_user(sign_up_email, sign_up_password, sign_up_name)
            if user_data:
                new_user_session = authentificated_session(user_data)
                return new_user_session, "Registration successful"

            return {}

        raise PreventUpdate

    @_app.callback(
        [Output('users-report-div', 'children'),
         Output('predictions-report-div', 'children'),
         Output('credits-report-div', 'children')],
        [Input('refresh-button', 'n_clicks')],
        State('user-session', 'data'),
    )

    @_app.callback(
        [
            Output('deposit-amount', 'value'),
            Output('current-balance-billing', 'children')
        ],
        [
            Input('deposit-button', 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('deposit-amount', 'value'),
        ]
    )
    def manage_deposit(deposit_clicks, user_session, _deposit_amount):
        if deposit_clicks > 0 and _deposit_amount and _deposit_amount > 0:
            transaction_info = deposit_amount(_deposit_amount, user_session=user_session)

            if transaction_info:
                balance = fetch_user_balance(user_session=user_session)
                return "", html.H3(f"Balance: ({balance})")

        raise PreventUpdate

    @_app.callback(
        [Output('model-dropdown', 'options'),
         Output('model-dropdown', 'value'),
         ],
        Input('model-dropdown', 'options'),
        State('user-session', 'data')
    )
    def manage_models(_, user_session):
        models = fetch_models(user_session)
        dropdown_options = [{'label': model['name'], 'value': model['name']} for model in models]
        return dropdown_options, dropdown_options[0]['value']

    @_app.callback(
        [
            Output('prediction-history-table', 'children'),
            Output('current-balance-predictions', 'children')
        ],
        [
            Input('predict-button', 'n_clicks'),
        ],
        [
            State('user-session', 'data'),
            State('model-dropdown', 'value'),
            State({'type': 'input-merchant', 'index': ALL}, 'value'),
            State({'type': 'input-cluster', 'index': ALL}, 'value'),
        ]
    )
    def manage_predictions(n_clicks, user_session, selected_model, merchant_ids, cluster_ids):
        if n_clicks > 0 and user_session:
            send_prediction_request(selected_model, merchant_ids, cluster_ids, user_session)
            predictions = fetch_prediction_history(user_session=user_session)
            balance = fetch_user_balance(user_session=user_session)
            return prediction_history_table(predictions), html.H3(f"Balance: ({balance})")

        raise PreventUpdate

    @_app.callback(
        Output('merchant-cluster-pairs', 'children'),
        [Input('add-pair-button', 'n_clicks'),
         Input({'type': 'remove-pair', 'index': ALL}, 'n_clicks')],
        [State('merchant-cluster-pairs', 'children')]
    )
    def manage_merchant_pairs(_, __, children):
        def get_index_from_prop_id(prop_id):
            try:
                json_part = prop_id.split('.n_clicks')[0]
                json_part = json_part.replace("'", "\"")
                prop_id_dict = json.loads(json_part)
                return int(prop_id_dict.get("index"))
            except (ValueError, json.JSONDecodeError):
                return None

        ctx = callback_context

        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'add-pair-button':
            new_index = len(children)
            children.append(create_merchant_cluster_pair(new_index))
            return children

        elif 'remove-pair' in button_id:
            indices_to_remove = [get_index_from_prop_id(trigger['prop_id']) for trigger in ctx.triggered if
                                 'remove-pair' in trigger['prop_id']]
            indices_to_remove = [index for index in indices_to_remove if index is not None]

            if indices_to_remove:
                return [child for i, child in enumerate(children) if i not in indices_to_remove]

        raise PreventUpdate

    @_app.callback(
        Output('estimated-cost', 'children'),
        [Input('model-dropdown', 'value'),
         Input('merchant-cluster-pairs', 'children')],
        [State('user-session', 'data')]
    )
    def update_estimated_cost(selected_model, merchant_pairs, user_session):
        global_models = fetch_models(user_session=user_session)
        if selected_model and merchant_pairs and global_models:
            num_pairs = len(merchant_pairs)
            total_cost = 0

            for model in global_models:
                if model['name'] == selected_model:
                    total_cost = model['cost'] * max(num_pairs, 1)
                    break
            return estimated_cost(total_cost)
        return estimated_cost(None)
