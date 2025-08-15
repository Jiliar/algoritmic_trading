import backtrader as bt
import matplotlib as plt1
plt1.use('inline')
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd

import plotly.graph_objects as go
import pandas as pd

def plotly_candlestick_with_pdh_pdl(csv_path, pdh_points=None, pdl_points=None, darkmode=False, from_date=None, to_date=None):
    """Versión que extiende las líneas de PDH/PDL del viernes hasta el lunes"""
    
    # 1. Cargar y preparar los datos
    df = pd.read_csv(csv_path)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        raise ValueError('El archivo CSV debe tener una columna llamada "date"')

    # 2. Crear el gráfico de velas
    data = [
        go.Candlestick(
            x=df['date'],
            open=df['open'], high=df['high'],
            low=df['low'], close=df['close'],
            increasing_line_color='cyan' if darkmode else 'green',
            decreasing_line_color='gray' if darkmode else 'red',
            name='Precio'
        )
    ]
    
    # 3. Configurar líneas y anotaciones para PDH/PDL
    shapes = []
    annotations = []
    
    def add_levels(points, color, label):
        nonlocal shapes, annotations
        if points:
            for dt, value in points:
                dt_obj = pd.to_datetime(dt)
                if (from_date and dt_obj < pd.to_datetime(from_date)) or (to_date and dt_obj > pd.to_datetime(to_date)):
                    continue
                
                # Definir el inicio del día
                start_of_day = dt_obj.normalize()

                # ⭐ Lógica de extensión de línea de viernes a lunes
                if dt_obj.weekday() == 4:  # 4 = viernes
                    # Extender la línea 3 días para cubrir sábado y domingo
                    end_of_line = start_of_day + pd.Timedelta(days=3)
                else:
                    # La línea dura un día para los demás días de la semana
                    end_of_line = start_of_day + pd.Timedelta(days=1)
                
                shapes.append(dict(
                    type='line',
                    x0=start_of_day,
                    x1=end_of_line,
                    y0=value, y1=value,
                    line=dict(color=color, width=1, dash='dot')
                ))
                
                annotations.append(dict(
                    x=dt_obj, y=value,
                    text=f'{label} - {dt_obj.strftime("%m-%d")}<br>[{value:.5f}]',
                    showarrow=False,
                    font=dict(color=color, size=10),
                    xanchor='right'
                ))
    
    add_levels(pdh_points, '#39FF14', 'PDH')
    add_levels(pdl_points, 'magenta', 'PDL')

    # 4. Crear y mostrar el gráfico
    fig = go.Figure(data=data, layout=go.Layout(
        template='plotly_dark' if darkmode else 'plotly_white',
        title='Candlestick con PDH/PDL',
        shapes=shapes,
        annotations=annotations,
        yaxis_title='Precio',
        xaxis_title='Fecha',
        width=1600,
        height=800,
        xaxis=dict(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
    ))
    
    price_range = df['high'].max() - df['low'].min()
    fig.update_yaxes(range=[
        max(df['low'].min() - price_range * 0.1, 0),
        df['high'].max() + price_range * 0.1
    ])

    fig.show()

def run_backtest(strategy, cash, datapath, from_date, to_date,
                 datetime_idx=0, open_idx=1, high_idx=3, low_idx=2,
                 close_idx=4, volume_idx=5, openinterest_idx=-1,
                 dtformat='%Y-%m-%d %H:%M:%S', commission=0.001, 
                 stake=None, plot='matplotlib', plot_engine='inline', 
                 darkmode=False, indicator=None,
                 pdh_points=None, pdl_points=None):
    """
    Ejecuta un backtest en Backtrader y permite graficar con Matplotlib o Plotly.
    Si plot='plotly', grafica velas y líneas PDH/PDL si se proveen.
    """
    cerebro = bt.Cerebro()
    cerebro.addstrategy(strategy)
    if stake is not None:
        cerebro.addsizer(bt.sizers.FixedSize, stake=stake)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    print(f"Data Path: {datapath}")
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=dtformat,
        datetime=datetime_idx,
        open=open_idx,
        high=high_idx,
        low=low_idx,
        close=close_idx,
        volume=volume_idx,
        fromdate=from_date,
        todate=to_date,
        reverse=False
    )
    cerebro.adddata(data)
    if indicator:
        cerebro.addindicator(indicator)
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    if plot == 'matplotlib':
        if plot_engine == 'inline':
            try:
                from IPython import get_ipython
                ipy = get_ipython()
                if ipy is not None:
                    plt.use('module://matplotlib_inline.backend_inline', force=True)
            except Exception:
                pass
        elif plot_engine == 'widget':
            try:
                from IPython import get_ipython
                ipy = get_ipython()
                if ipy is not None:
                    plt.use('module://ipympl.backend_nbagg', force=True)
            except Exception:
                pass
        if darkmode:
            plt.style.use('dark_background')
        figs_axes = cerebro.plot(style='candlestick', barup='cyan' if darkmode else 'green', bardown='gray' if darkmode else 'red', volume=False, iplot=False)
    elif plot == 'plotly':
        plotly_candlestick_with_pdh_pdl(
            datapath, 
            pdh_points, 
            pdl_points, 
            darkmode=darkmode,
            from_date=from_date,
            to_date=to_date
        )
    if pdh_points:
        for i, pdh in enumerate(pdh_points):
            if i == 0:
                continue
            prev_date = pdh_points[i-1]['date'] if isinstance(pdh_points[i-1], dict) else pdh_points[i-1][0]
            curr_date = pdh['date'] if isinstance(pdh, dict) else pdh[0]
            # No saltar ningún día, incluidos sábados
            start_date = dt_to_str(prev_date)
            end_date = dt_to_str(curr_date)
            price = pdh['price'] if isinstance(pdh, dict) else pdh[1]
            if not start_date or not end_date:
                continue
            shapes.append(dict(
                type='line',
                x0=start_date, x1=end_date,
                y0=price, y1=price,
                xref='x', yref='y',
                line=dict(color='cyan', width=1, dash='dot')
            ))
            annotations.append(dict(
                x=start_date, y=price, xref='x', yref='y',
                showarrow=False, xanchor='right',
                text=f"PDH ({start_date})", font=dict(color='cyan')
            ))
    if pdl_points:
        for i, pdl in enumerate(pdl_points):
            if i == 0:
                continue
            prev_date = pdl_points[i-1]['date'] if isinstance(pdl_points[i-1], dict) else pdl_points[i-1][0]
            curr_date = pdl['date'] if isinstance(pdl, dict) else pdl[0]
            # No saltar ningún día, incluidos sábados
            start_date = dt_to_str(prev_date)
            end_date = dt_to_str(curr_date)
            price = pdl['price'] if isinstance(pdl, dict) else pdl[1]
            if not start_date or not end_date:
                continue
            shapes.append(dict(
                type='line',
                x0=start_date, x1=end_date,
                y0=price, y1=price,
                xref='x', yref='y',
                line=dict(color='magenta', width=1, dash='dot')
            ))
            annotations.append(dict(
                x=start_date, y=price, xref='x', yref='y',
                showarrow=False, xanchor='right',
                text=f"PDL ({start_date})", font=dict(color='magenta')
            ))