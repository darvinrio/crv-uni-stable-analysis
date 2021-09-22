import pandas as pd
import numpy as np 
from datetime import datetime as dt

from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource as cds
from bokeh.models import HoverTool
from bokeh.models import NumeralTickFormatter
from bokeh.models import Range1d, Span

color_dict = {
    'DAI':'#f4b731',
    'USDC':'#256fc0',
    'USDT':'#259c77',
    'TOTAL':'#454a75'
} 

import os 
dirname = 'app' #os.path.basename(os.path.dirname(__file__))
print(dirname)

# read csv
crv_liq_df = pd.read_csv(dirname+'/data/3pool-liq.csv')
uni_liq_df = pd.read_csv(dirname+'/data/uni_stable-liq.csv')
crv_swap_df = pd.read_csv(dirname+'/data/3pool_swaps.csv')
uni_swap_df = pd.read_csv(dirname+'/data/uni-stableswaps.csv')



#prep data
crv_liq_df['BALANCE_DATE'] = pd.to_datetime(crv_liq_df['BALANCE_DATE']).dt.tz_localize(None)
crv_liq_df=crv_liq_df.sort_values('BALANCE_DATE')

uni_liq_df['BALANCE_DATE'] = pd.to_datetime(uni_liq_df['BALANCE_DATE']).dt.tz_localize(None)
uni_liq_token_df = uni_liq_df.groupby(['BALANCE_DATE','SYMBOL'], as_index = False)['BALANCE'].sum()
uni_liq_token_df = uni_liq_token_df.sort_values('BALANCE_DATE')

crv_liq_all_df = crv_liq_df.groupby(['BALANCE_DATE'], as_index = False)['BALANCE'].sum()
crv_liq_all_df['DEX'] = 'CURVE'
crv_liq_all_df['COLOR'] = '#008000'
crv_liq_all_df.head()

uni_liq_all_df = uni_liq_df.groupby(['BALANCE_DATE'], as_index = False).sum()
uni_liq_all_df['DEX'] = 'UNISWAP'
uni_liq_all_df['COLOR'] = '#fc077d'
uni_liq_all_df.head()

tvl_df = pd.concat([crv_liq_all_df,uni_liq_all_df])

curve_slip = crv_swap_df['SLIPPAGE']
arr_slip, edges = np.histogram(curve_slip,
                              bins=int(0.4/0.002),
                              range = [-0.2, 0.2])
curve_slip_df = pd.DataFrame({
    'txs':arr_slip,
    'left': edges[:-1], 
    'right': edges[1:],
    'label_left': edges[:-1]/100, 
    'label_right': edges[1:]/100
})

uni_slip = uni_swap_df['SLIPPAGE']
arr_slip, edges = np.histogram(uni_slip,
                              bins=int(0.4/0.002),
                              range = [-0.2, 0.2])
uni_slip_df = pd.DataFrame({
    'txs':arr_slip,
    'left': edges[:-1], 
    'right': edges[1:],
    'label_left': edges[:-1]/100, 
    'label_right': edges[1:]/100
})
uni_slip_df.head()

uni_slip_df['DEX']='UNISWAP'
uni_slip_df['tx_propotion'] = uni_slip_df['txs']/uni_slip_df['txs'].sum()
curve_slip_df['DEX']='CURVE'
curve_slip_df['tx_propotion'] = curve_slip_df['txs']/curve_slip_df['txs'].sum()
slip_df = pd.concat([curve_slip_df,uni_slip_df])

slip_stat_df = pd.DataFrame([uni_slip.describe(),curve_slip.describe()])
slip_stat_df.index=['UNISWAP','CURVE']

#plots

p = figure(x_axis_type='datetime',x_axis_label='Time',y_axis_label='TVL_USD'
          ,sizing_mode="scale_width",name='curve_token_plot')

for token in list(crv_liq_df['SYMBOL'].unique()):
    if token=='TOTAL':
        continue
    p.line(source=cds(crv_liq_df[crv_liq_df['SYMBOL']==token]), 
           x='BALANCE_DATE',y='BALANCE',color =color_dict[token],line_width=2,legend_label=token)
    
hover = HoverTool(tooltips = [('Date', '@BALANCE_DATE{%F | %R}'),
                             ('Liquidity', '@BALANCE{($ 0.00 a)}'),
                             ('Symbol','@SYMBOL')],
                 formatters={'@BALANCE_DATE': 'datetime'},mode='vline')

p.yaxis.formatter=NumeralTickFormatter(format="$ 0.00 a")
p.add_tools(hover)
p.axis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.legend.click_policy="hide"
curve_token_plot=p


p = figure(x_axis_type='datetime',x_axis_label='Time',y_axis_label='TVL_USD'
          ,sizing_mode="scale_width",name='uni_token_plot')

for token in list(uni_liq_token_df['SYMBOL'].unique()):
    if token=='TOTAL':
        continue
    p.line(source=cds(uni_liq_token_df[uni_liq_token_df['SYMBOL']==token]), 
           x='BALANCE_DATE',y='BALANCE',color =color_dict[token],line_width=2,legend_label=token)
    
hover = HoverTool(tooltips = [('Date', '@BALANCE_DATE{%F | %R}'),
                             ('Liquidity', '@BALANCE{($ 0.00 a)}'),
                             ('Symbol','@SYMBOL')],
                 formatters={'@BALANCE_DATE': 'datetime'},mode='vline')

p.yaxis.formatter=NumeralTickFormatter(format="$ 0.00 a")
p.add_tools(hover)
p.axis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.legend.click_policy="hide"
uni_token_plot=p


p = figure(plot_height=300, x_axis_type='datetime',x_axis_label='Time',y_axis_label='TVL_USD'
          ,sizing_mode="stretch_width",name='liq_comp_plot')

for token in list(tvl_df['DEX'].unique()):
    print(token)
    p.line(source=cds(tvl_df[tvl_df['DEX']==token]), 
           x='BALANCE_DATE',y='BALANCE',color= '#fc077d' if token=='UNISWAP' else '#008000',
           line_width=2,legend_label=token)
    
hover = HoverTool(tooltips = [('Date', '@BALANCE_DATE{%F | %R}'),
                             ('Liquidity', '@BALANCE{($ 0.00 a)}'),
                             ('DEX','@DEX')],
                 formatters={'@BALANCE_DATE': 'datetime'},mode='vline')

p.yaxis.formatter=NumeralTickFormatter(format="$ 0.00 a")
p.add_tools(hover)
p.axis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.legend.click_policy="hide"
liq_comp_plot = p

p = figure(plot_height=300,x_axis_label = 'Slippage', 
           y_axis_label = 'Number of Swaps',sizing_mode="scale_width",name='curve_slip_plot')

# Add a quad glyph
p.quad(source=cds(curve_slip_df),bottom=0, top='txs', 
       left='left', right='right',fill_color='#008000',line_color='#008000',fill_alpha=0.7,
       hover_fill_color='#008000',hover_fill_alpha=1)

hover = HoverTool(tooltips = [('Slippage ', '@label_left{:.000%} to @label_right{:.000%}'),
                          ('Number of Swaps', '@txs')])
p.yaxis.visible = False
p.add_tools(hover)
p.grid.grid_line_color = None
p.outline_line_color = None
p.x_range = Range1d(-0.2,0.2)
curve_slip_plot=p


p = figure(plot_height=300,x_axis_label = 'Slippage', 
           y_axis_label = 'Number of Swaps',sizing_mode="scale_width",name='uni_slip_plot')

# Add a quad glyph
p.quad(source=cds(uni_slip_df),bottom=0, top='txs', 
       left='left', right='right',fill_color= '#fc077d',line_color='#fc077d',fill_alpha=0.7,
       hover_fill_color='#fc077d',hover_fill_alpha=1)

hover = HoverTool(tooltips = [('Slippage ', '@label_left{:.000%} to @label_right{:.000%}'),
                          ('Number of Swaps', '@txs')])
p.add_tools(hover)
p.yaxis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.x_range = Range1d(-0.2,0.2)
uni_slip_plot=p


p = figure(plot_height=300,x_axis_label = 'Slippage', 
           y_axis_label = 'Number of Swaps',sizing_mode="scale_width",name='comp_slip_plot')


for token in list(slip_df['DEX'].unique()):
    p.quad(source=cds(slip_df[slip_df['DEX']==token]),bottom=0, top='tx_propotion', 
           left='left', right='right',fill_color= '#fc077d' if token=='UNISWAP' else '#008000',line_color='#fc077d' if token=='UNISWAP' else '#008000',
           fill_alpha = 0.5,hover_fill_color='#fc077d' if token=='UNISWAP' else '#008000',
           hover_fill_alpha=1,legend_label=token)

hover = HoverTool(tooltips = [('Slippage ', '@label_left{:.000%} to @label_right{:.000%}'),
                          ('Percent of swaps', '@tx_propotion{:.000%}'),
                             ('DEX', '@DEX')])
p.add_tools(hover)
p.yaxis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.x_range = Range1d(-0.2,0.2)
p.legend.click_policy="hide"
comp_slip_plot=p

p = figure(plot_height=300,x_axis_label = 'Slippage', 
           y_axis_label = 'Number of Swaps',sizing_mode="scale_width",name='uni_slip_stat_plot')

# Add a quad glyph
p.quad(source=cds(uni_slip_df),bottom=0, top='txs', 
       left='left', right='right',fill_color= '#fc077d',line_color='#fc077d',fill_alpha=0.7,
       hover_fill_color='#fc077d',hover_fill_alpha=1)

for stat in slip_stat_df.columns:
        if stat in ['count','std','min','max']:
            continue
        val = slip_stat_df[stat]['UNISWAP']
        val_span = Span(location=val,dimension='height', line_color='black',
                     line_width=2)
        p.add_layout(val_span)

hover = HoverTool(tooltips = [('Slippage ', '@label_left{:.000%} to @label_right{:.000%}'),
                          ('Number of Swaps', '@txs')])
p.add_tools(hover)
p.yaxis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.x_range = Range1d(-0.1,0.1)
uni_slip_stat_plot=p


p = figure(plot_height=300,x_axis_label = 'Slippage', 
           y_axis_label = 'Number of Swaps',sizing_mode="scale_width",name='curve_slip_stat_plot')

# Add a quad glyph
p.quad(source=cds(curve_slip_df),bottom=0, top='txs', 
       left='left', right='right',fill_color= '#008000',line_color='#008000',fill_alpha=0.7,
       hover_fill_color='#008000',hover_fill_alpha=1)

for stat in slip_stat_df.columns:
        if stat in ['count','std','min','max']:
            continue
        val = slip_stat_df[stat]['CURVE']
        val_span = Span(location=val,dimension='height', line_color='black',
                     line_width=2)
        p.add_layout(val_span)

hover = HoverTool(tooltips = [('Slippage ', '@label_left{:.000%} to @label_right{:.000%}'),
                          ('Number of Swaps', '@txs')])
p.add_tools(hover)
p.yaxis.visible = False
p.grid.grid_line_color = None
p.outline_line_color = None
p.x_range = Range1d(-0.1,0.1)
curve_slip_stat_plot=p

def get_plot():
    return curve_token_plot,uni_token_plot,liq_comp_plot,curve_slip_plot,uni_slip_plot,comp_slip_plot,uni_slip_stat_plot,curve_slip_stat_plot