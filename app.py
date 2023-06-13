import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.stats.proportion as sp
from pandas.api.types import is_numeric_dtype

st.set_page_config(page_title='Churn Dashboard', layout='wide', initial_sidebar_state='expanded')
st.title('PowerCo Churn Dashboard')
st.markdown("""
The dashboard forecasts customer churn for PowerCo, visualizes churn risk across categories, and identifies top at-risk customers for strategic retention planning.
""")
st.markdown("<h3></h3><h3></h3>", unsafe_allow_html=True)

#st.markdown("<h3></h3>", unsafe_allow_html=True)

colors = ['#f03e3e', '#4dabf7']

##---- data ----##
df =  pd.read_parquet(r'C:\Users\Eric\Documents\___Portfolio\bcg-churn\data\preds.parquet')

##---- Metrics ----##

# churn rate/retentation rate
churn_rate = df['churn'].mean()
retention_rate = (1 - churn_rate)

# monthly revenue for the next 12 months
monthly_revenue = (df['base_revenue'] / 12).sum()

# Number of customers at-risk
customers_at_risk = df.query('pred==1')['id'].count()

# revenue amount at-risk
revenue_at_risk = df.query('pred==1')['base_revenue'].sum()


def format_value(value):
    if value >= 1000000:
        return f'{value/1000000:.1f}M'
    elif value >= 1000:
        return f'{value/1000:.1f}K'
    else:
        return str(value)

def display_metrics(revenue_at_risk, customers_at_risk, retention_rate, another_metric):
    col1, col2, col3, col4 = st.columns(4)
    
    if revenue_at_risk is not None:
        col1.metric(label="Revenue at-risk", value=format_value(revenue_at_risk))
    if customers_at_risk is not None:
        col2.metric(label="Number of Risky Customers", value=format_value(customers_at_risk))
    if retention_rate is not None:
        col3.metric(label="Customer Retention Rate", value=f"{retention_rate:.0%}")
    if another_metric is not None:
        col4.metric(label="MMR", value=format_value(monthly_revenue))


### --- Histogram --- ###
def plot_hist(df, col, use_category_orders=False):
    if not is_numeric_dtype(df[col]):
        df[col] = pd.Categorical(df[col], ordered=True)  # Convert column to ordered categorical
    
    category_orders = None
    if use_category_orders:
        category_orders = {col: df[col].cat.categories}
    
    fig = px.histogram(df, x=col, category_orders=category_orders)
    fig.update_traces(marker_color=colors[1], opacity=0.9)
    fig.update_layout(
        title=f'Distribution of {col}',
        xaxis_title=f'{col}',
        yaxis_title='Count',
        showlegend=False,
        bargap=0.1,
        plot_bgcolor='white',
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=1
        ),
        yaxis=dict(
            #gridcolor='lightgray',
        ),
    )

    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=False,
    )

    fig.update_yaxes(
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=True,
        #gridcolor='lightgray'
    )

    return fig

### --- Churn risk across categories--- ###
def category_churn_summary(churn_data, cat_col, target):
    summary = churn_data.groupby(cat_col).agg({cat_col:'count', target: ['sum','mean']})
    intervals = sp.proportion_confint(summary[target,'sum'],summary[(cat_col,'count')], method='wilson')
    summary[cat_col + '_percent'] = (1.0/churn_data.shape[0]) * summary[(cat_col,'count')]
    summary['lo_conf'] = intervals[0]
    summary['hi_conf'] = intervals[1]
    summary['lo_int'] = summary[(target,'mean')] - summary['lo_conf']
    summary['hi_int'] = summary['hi_conf'] - summary[(target,'mean')]
    return summary

def plot_churn_risk(summary, cat_col, target):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=list(summary.index),
            y=[0.1] * len(summary.index),
            mode='lines',
            line=dict(color='red', dash='dash', width=2),
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=list(summary.index),
            y=summary[(target, 'mean')],
            mode='markers+text',
            text=[f"{y_val:.0%}" for y_val in summary[(target, 'mean')]],
            textposition='middle center',
            textfont=dict(color='white', size=12),
            marker=dict(color=summary[(target, 'mean')], size=35, colorscale='gnbu'),
        )
    )
    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=14),
        #gridcolor='lightgray'
    )

    fig.update_yaxes(
        tickformat='.0%',
        #range=[0, 0.2],
        tickfont=dict(size=12),
        title_font=dict(size=14),
        #gridcolor='lightgray'
    )
    fig.update_layout(
        title=f'Churn risk vs {cat_col}',
        xaxis_title=cat_col,
        yaxis_title='Churn Risk',
        plot_bgcolor='white',
        xaxis=dict(
            tickmode='array',
            tickvals=list(summary.index),
            tickfont=dict(size=14),
        ),
        yaxis=dict(
            tickformat=".0%",
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        showlegend=False,
    )

    return fig

### --- Churn risk across categoricals --- ###
def plot_cat_churn_risk(df, col, target):
    proportions = pd.crosstab(df[col], df[target], normalize='index')
    proportions = proportions.rename(columns={0: 'No', 1: 'Yes'})
    
    fig = px.bar(
        proportions,
        x=proportions.index,
        y=['Yes', 'No'],
        color_discrete_sequence=[colors[0], colors[1]],
        barmode='stack',
        title=f'Churn Risk By {col}',
    )
    
    fig.add_shape(
        type='line',
        x0=-0.5,
        y0=0.1,
        x1=len(df[col].unique())-.5,
        y1=0.1,
        line=dict(color='red', dash='dash', width=2),
    )
    
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        plot_bgcolor='white',
        legend_title='Churn Status',
    )

    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=False,
        #gridcolor='lightgray'
    )

    fig.update_yaxes(
        tickformat='.0%',
        range=[0, 0.2],
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=False,
        #gridcolor='lightgray'
    )

    fig.update_traces(
        opacity=0.9,
        hovertemplate="Category: %{x}<br>Churn Risk: %{y:.0%}",
        #texttemplate='%{y:.0%}',
        textposition='auto',
        textfont=dict(color='white', size=14,family='Arial')
    )

    return fig
### --- Average revenue across categories--- ###
def plot_grouped_bars(df, cat_col, cont_col, target):
    fig = px.histogram(
        df,
        x=cat_col,
        y=cont_col,
        histfunc='avg',
        color=target,
        barmode='group',
        title=f'Distribution of Yearly Revenue by {cat_col} and Churn',
        color_discrete_map={0: colors[1], 1: colors[0]}
    )
    fig.update_layout(
        xaxis_title='',
        yaxis_title= f'{cont_col}',
        legend_title='Churn Status',
        plot_bgcolor='white',
        showlegend=False
    )

    fig.update_xaxes(
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=False
    )

    fig.update_yaxes(
        tickformat=',d',
        tickfont=dict(size=12),
        title_font=dict(size=14),
        showgrid=True,
        gridcolor='lightgray'
    )

    fig.update_traces(
        opacity=0.9,
        hovertemplate="Categorie: %{x}<br>Revenue: %{y:$,.0f}",
        textposition='inside',
        textfont=dict(color='white', size=14,family='Arial'),
        texttemplate='%{y:$,.0f}',
        marker=dict(line=dict(width=0))
    )

    return fig


# App layout
# First row: Metrics
display_metrics(revenue_at_risk, customers_at_risk, retention_rate, monthly_revenue)        

# Second row: Churn Risk and Distribution
option = st.selectbox(
    'Select feature:',
    ('years_as_client', 'n_actv_ps', 'base_revenue_cat','forecast_discount_energy'))
col1, col2 = st.columns([3,2])
with col1:       
    summary_ps = category_churn_summary(df, option, 'churn')
    st.plotly_chart(plot_churn_risk(summary_ps, option, 'churn'), use_container_width=True, width=400)    

with col2:
    col2.markdown(
    f"""
    <style>
    .custom-column-height {{
        height: 0px;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )      
    st.plotly_chart(plot_hist(df, option), use_container_width=True)

# Third row: Average Revenue by categorical and Churnk Risk vs Categorical
option2 = st.selectbox(
    'Select feature:',
    ('sales_channel_id', 'first_ec_id',))

col3, col4 = st.columns([4,2.5])

with col3:
    st.plotly_chart(plot_grouped_bars(df, option2, 'base_revenue', 'churn'), use_container_width=True)

with col4:
    st.plotly_chart(plot_cat_churn_risk(df, option2, 'churn'), use_container_width=True)


# Display a preview of the filtered dataframe
st.subheader('Top 10 customer at-risk')
# Create a styler object and apply background gradient to the 'proba' column

def highlight_high_proba(val):
    """
    Takes a scalar and returns a string with a CSS color gradient for high proba values
    """
    if val > 0.90:
        color = f'linear-gradient(to right, red {val*100}%, white {val*100}%)'
    else:
        color = 'white'
    return f'background: {color}'

#### cmap ####
from matplotlib.colors import ListedColormap
# Define the base color
base_color = '#f03e3e'

# Generate a lighter shade of the base color
light_color = '#FFAAAA'

# Create a colormap with the base color and the lighter shade
custom_cmap = ListedColormap([light_color, base_color])
######


st.dataframe(
    df.sort_values(by='proba', ascending=False).head(10).style.background_gradient(subset='proba',cmap=custom_cmap),
    column_order=('id', 'proba', 'base_revenue', 'sales_channel_id','n_actv_ps','years_as_client'),
    column_config={
        'id':'Customer ID',
        'proba': st.column_config.NumberColumn(
            "Risk",
            format="%.2f"
        ),
        'base_revenue': st.column_config.NumberColumn(
            "Revenue in EUR",
            format="%.2f"
        ),
        'sales_channel_id':'Sales Channel',
        'n_actv_ps':'Products Active',
        'years_as_client':'Years as Client'
    },
    hide_index=True,
    use_container_width=True

)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
#st.markdown(hide_st_style, unsafe_allow_html=True)