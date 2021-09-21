from bokeh.io import curdoc

from scripts.graphs import get_plot

print('app loaded')

curve_token_plot,uni_token_plot,liq_comp_plot,curve_slip_plot,uni_slip_plot,comp_slip_plot = get_plot()

curdoc().add_root(curve_token_plot)
curdoc().add_root(uni_token_plot)
curdoc().add_root(liq_comp_plot)
curdoc().add_root(curve_slip_plot)
curdoc().add_root(uni_slip_plot)
curdoc().add_root(comp_slip_plot)

curdoc().title = 'Curve vs Uniswap'