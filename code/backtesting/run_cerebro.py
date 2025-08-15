import backtrader as bt
import matplotlib as plt
plt.use('inline')

def run_backtest(strategy, cash, datapath, from_date, to_date,
                 datetime_idx=0, open_idx=1, high_idx=3, low_idx=2,
                 close_idx=4, volume_idx=5, openinterest_idx=-1,
                 dtformat='%Y-%m-%d %H:%M:%S', commission=0.001, 
                 stake=None, plot=False, plot_engine='inline', darkmode=False):

    """
    Ejecuta un backtest en Backtrader con parámetros configurables.

    Parámetros:
        strategy (bt.Strategy): Clase de estrategia a ejecutar.
        cash (float): Capital inicial del broker.
        datapath (str): Ruta al archivo CSV con datos históricos.
        from_date (datetime.date): Fecha de inicio de los datos.
        to_date (datetime.date): Fecha de fin de los datos.
        datetime_idx (int): Índice de la columna fecha/hora.
        open_idx (int): Índice de la columna precio de apertura.
        high_idx (int): Índice de la columna precio máximo.
        low_idx (int): Índice de la columna precio mínimo.
        close_idx (int): Índice de la columna precio de cierre.
        volume_idx (int): Índice de la columna volumen.
        openinterest_idx (int): Índice de la columna open interest (-1 si no aplica).
        dtformat (str): Formato de fecha/hora en el CSV.
        commission (float): Comisión por operación (ej. 0.001 para 0.1%).
    """

    def customize_crosshair(ax):
        import mplcursors
        import numpy as np

        # Assume the main plotted line is the first line in the axes
        lines = ax.get_lines()
        if not lines:
            return
        line = lines[0]
        xdata = line.get_xdata()
        ydata = line.get_ydata()

        # Create horizontal and vertical lines for crosshair
        hline = ax.axhline(color='lightgray', linestyle=':', lw=1)
        vline = ax.axvline(color='lightgray', linestyle=':', lw=1)

        def on_move(sel):
            x = sel.target[0]
            # Find closest index for xdata
            if len(xdata) == 0:
                return
            idx = np.searchsorted(xdata, x)
            if idx == 0:
                y = ydata[0]
            elif idx >= len(xdata):
                y = ydata[-1]
            else:
                # Linear interpolation
                x0, x1 = xdata[idx-1], xdata[idx]
                y0, y1 = ydata[idx-1], ydata[idx]
                if x1 == x0:
                    y = y0
                else:
                    y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
            hline.set_ydata(y)
            vline.set_xdata(x)
            ax.figure.canvas.draw_idle()

        cursor = mplcursors.cursor(line, hover=True)
        cursor.connect("add", on_move)
        return cursor

    def apply_dark_mode():
        plt.style.use('dark_background')
        plt.rcParams['axes.facecolor'] = 'black'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        plt.rcParams['grid.color'] = 'lightgray'
        plt.rcParams['grid.linestyle'] = '--'
        plt.gca().yaxis.grid(True)
        plt.gca().xaxis.grid(False)
        # Set main candlestick price axis y-axis tick labels to black
        ax = plt.gca()
        # Only set the ytick labels color to black for the main price axis
        # Check if this is the main axis by looking at its label or other properties
        # Assuming main axis has label 'Price' or similar, but since label is not set, just set ytick labels color to black
        for label in ax.get_yticklabels():
            label.set_color('white')

    def apply_light_mode():
        plt.rcParams['grid.color'] = 'lightgray'
        plt.rcParams['grid.linestyle'] = '--'
        plt.gca().yaxis.grid(True)
        plt.gca().xaxis.grid(False)

    # Crea instancia del motor de Backtrader
    cerebro = bt.Cerebro()


    # Añade la estrategia
    cerebro.addstrategy(strategy)

    # Si stake está definido, añade un sizer FixedSize
    if stake is not None:
        cerebro.addsizer(bt.sizers.FixedSize, stake=stake)

    # Establece el capital inicial
    cerebro.broker.setcash(cash)

    # Establece la comisión del broker (0.1% por defecto)
    cerebro.broker.setcommission(commission=commission)

    # Muestra la ruta de datos
    print(f"Data Path: {datapath}")

    # Configura el feed de datos
    data = bt.feeds.GenericCSVData(
        dataname=datapath,
        dtformat=dtformat,
        datetime=datetime_idx,
        open=open_idx,
        high=high_idx,
        low=low_idx,
        close=close_idx,
        volume=volume_idx,
        openinterest=openinterest_idx,
        fromdate=from_date,
        todate=to_date,
        reverse=False
    )

    # Añade los datos al cerebro
    cerebro.adddata(data)

    # Estado inicial del portafolio
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")

    # Ejecuta el backtest
    cerebro.run()

    # Estado final del portafolio
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

    # Si plot es True, mostrar el gráfico
    if plot:
        import matplotlib
        import matplotlib.pyplot as plt
        # Cambia el backend según plot_engine
        if plot_engine == 'inline':
            try:
                from IPython import get_ipython
                ipy = get_ipython()
                if ipy is not None:
                    matplotlib.use('module://matplotlib_inline.backend_inline', force=True)
            except Exception:
                pass
        elif plot_engine == 'widget':
            try:
                from IPython import get_ipython
                ipy = get_ipython()
                if ipy is not None:
                    matplotlib.use('module://ipympl.backend_nbagg', force=True)
            except Exception:
                pass
        # Puedes agregar más opciones de backend aquí si lo deseas
        if darkmode:
            apply_dark_mode()
            figs_axes = cerebro.plot(style='candlestick', barup='#39FF14', bardown='#FF00FF', volume=False, iplot=False)
            for fig, axes in figs_axes:
                for ax in axes:
                    customize_crosshair(ax)
        else:
            apply_light_mode()
            figs_axes =  figs_axes = cerebro.plot(style='candlestick', barup='green', bardown='red', volume=False, iplot=False)
            for fig, axes in figs_axes:
                for ax in axes:
                    customize_crosshair(ax)