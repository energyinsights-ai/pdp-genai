import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

def load_data(file_path):
    df = pd.read_csv(file_path)
    df['prod_date'] = pd.to_datetime(df['prod_date'])
    return df

def preprocess_data(df):
    # Group by well_api and filter wells with at least 24 months of data
    well_counts = df.groupby('well_api').size()
    valid_wells = well_counts[well_counts >= 24].index
    
    # Randomly select 10 wells from the valid wells
    selected_wells = np.random.choice(valid_wells, size=min(10, len(valid_wells)), replace=False)
    
    df_filtered = df[df['well_api'].isin(selected_wells)]
    
    # Sort data by well_api and prod_date
    df_filtered = df_filtered.sort_values(['well_api', 'prod_date'])
    
    return df_filtered

def arps_decline(t, qi, di, b):
    return qi / (1 + b * di * t) ** (1 / b)

def fit_arps_decline(time, production):
    # Initial guess for parameters
    p0 = [production.max(), 0.1, 0.5]
    
    # Fit the curve
    popt, _ = curve_fit(arps_decline, time, production, p0=p0, bounds=([0, 0, 0], [np.inf, 1, 2]))
    
    return popt

def forecast_well(well_data, forecast_months=12):
    # Prepare data for fitting
    time = (well_data['prod_date'] - well_data['prod_date'].min()).dt.days.values
    oil_production = well_data['oil'].values
    gas_production = well_data['gas'].values
    
    # Fit ARPS decline curve for oil and gas
    oil_params = fit_arps_decline(time, oil_production)
    gas_params = fit_arps_decline(time, gas_production)
    
    # Generate forecast
    forecast_time = np.arange(time[-1] + 30, time[-1] + 30 * (forecast_months + 1), 30)
    oil_forecast = arps_decline(forecast_time, *oil_params)
    gas_forecast = arps_decline(forecast_time, *gas_params)
    
    return oil_forecast, gas_forecast

def calculate_mpe(actual, forecast):
    return np.mean((forecast - actual) / actual) * 100

def evaluate_forecast(df):
    results = []
    for well in df['well_api'].unique():
        try:
            well_data = df[df['well_api'] == well]
            
            # Use all but last 12 months for training
            train_data = well_data.iloc[:-12]
            test_data = well_data.iloc[-12:]
            
            # Generate forecast
            oil_forecast, gas_forecast = forecast_well(train_data)
            
            # Calculate MPE for oil and gas
            oil_mpe = calculate_mpe(test_data['oil'].values, oil_forecast)
            gas_mpe = calculate_mpe(test_data['gas'].values, gas_forecast)
            
            results.append({
                'well_api': well,
                'oil_mpe': oil_mpe,
                'gas_mpe': gas_mpe
            })
        except Exception as e:
            print(f"Error processing well {well}: {str(e)}")
    
    return pd.DataFrame(results)

def plot_forecast(well_data, oil_forecast, gas_forecast):
    # Split data into training and test sets
    train_data = well_data.iloc[:-12]
    test_data = well_data.iloc[-12:]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=('Oil Production', 'Gas Production'))
    
    # Plot historical data (training set)
    fig.add_trace(go.Scatter(x=train_data['prod_date'], y=train_data['oil'], 
                             mode='markers', name='Oil Historical', marker_color='lightgreen'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=train_data['prod_date'], y=train_data['gas'], 
                             mode='markers', name='Gas Historical', marker_color='lightcoral'),
                  row=2, col=1)
    
    # Plot actual data for the forecast period (test set)
    fig.add_trace(go.Scatter(x=test_data['prod_date'], y=test_data['oil'], 
                             mode='markers', name='Oil Actual', marker_color='darkgreen'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=test_data['prod_date'], y=test_data['gas'], 
                             mode='markers', name='Gas Actual', marker_color='darkred'),
                  row=2, col=1)
    
    # Plot forecast
    forecast_dates = pd.date_range(start=train_data['prod_date'].iloc[-1] + pd.Timedelta(days=30), periods=12, freq='M')
    fig.add_trace(go.Scatter(x=forecast_dates, y=oil_forecast, mode='lines', 
                             name='Oil Forecast', line_color='green'),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=forecast_dates, y=gas_forecast, mode='lines', 
                             name='Gas Forecast', line_color='red'),
                  row=2, col=1)
    
    fig.update_layout(
        height=800, 
        title_text=f"Production Forecast for Well {well_data['well_api'].iloc[0]}",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    fig.update_xaxes(title_text="Date", row=2, col=1, showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(title_text="Oil Production (barrels of oil per month)", row=1, col=1, 
                     showgrid=True, gridcolor='lightgray', tickformat=',d')
    fig.update_yaxes(title_text="Gas Production", row=2, col=1, showgrid=True, gridcolor='lightgray')
    return fig

def plot_predicted_vs_actual(evaluation_results, df_filtered):
    # Prepare data for plotting
    plot_data = []
    for _, row in evaluation_results.iterrows():
        well_data = df_filtered[df_filtered['well_api'] == row['well_api']].iloc[-12:]
        oil_forecast, gas_forecast = forecast_well(df_filtered[df_filtered['well_api'] == row['well_api']].iloc[:-12])
        
        for actual_oil, pred_oil, actual_gas, pred_gas in zip(well_data['oil'], oil_forecast, well_data['gas'], gas_forecast):
            plot_data.append({
                'Actual Oil': actual_oil,
                'Predicted Oil': pred_oil,
                'Actual Gas': actual_gas,
                'Predicted Gas': pred_gas,
                'Well API': row['well_api']
            })
    
    plot_df = pd.DataFrame(plot_data)
    
    # Create oil scatter plot
    fig_oil = px.scatter(plot_df, x='Actual Oil', y='Predicted Oil', hover_data=['Well API'],
                         title='Predicted vs Actual Oil Production',
                         labels={'Actual Oil': 'Actual Oil Production (barrels/month)',
                                 'Predicted Oil': 'Predicted Oil Production (barrels/month)'},
                         color_discrete_sequence=['green'])
    fig_oil.add_trace(px.line(x=[0, plot_df['Actual Oil'].max()], y=[0, plot_df['Actual Oil'].max()]).data[0])
    
    # Create gas scatter plot
    fig_gas = px.scatter(plot_df, x='Actual Gas', y='Predicted Gas', hover_data=['Well API'],
                         title='Predicted vs Actual Gas Production',
                         labels={'Actual Gas': 'Actual Gas Production (units/month)',
                                 'Predicted Gas': 'Predicted Gas Production (units/month)'},
                         color_discrete_sequence=['red'])
    fig_gas.add_trace(px.line(x=[0, plot_df['Actual Gas'].max()], y=[0, plot_df['Actual Gas'].max()]).data[0])
    
    return fig_oil, fig_gas

def main(file_path):
    df = load_data(file_path)
    df_filtered = preprocess_data(df)
    evaluation_results = evaluate_forecast(df_filtered)
    
    print("Evaluation Results:")
    print(evaluation_results.describe())
    
    # Plot forecast for a sample well
    sample_well = df_filtered['well_api'].unique()[0]
    well_data = df_filtered[df_filtered['well_api'] == sample_well]
    oil_forecast, gas_forecast = forecast_well(well_data.iloc[:-12])
    fig = plot_forecast(well_data, oil_forecast, gas_forecast)
    fig.show()

if __name__ == "__main__":
    main("backend/well_prod.csv")