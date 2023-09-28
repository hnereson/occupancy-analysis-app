import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import altair as alt
import seaborn as sns
from matplotlib.colors import rgb2hex
import streamlit as st

class Plots():
    def __init__(self):
        self.font = 'monospace'

    def prepare_survival_data(self, df, start_time_column):
        unique_models = df['model'].unique()
        all_data = pd.DataFrame()

        for model in unique_models:
            model_data = df[df['model'] == model]
            kmf = KaplanMeierFitter()

            today = pd.Timestamp.now()
            T = np.where(model_data['moved_out_date'].isnull(),
                        (today - model_data[start_time_column]).dt.days,
                        (model_data['moved_out_date'] - model_data[start_time_column]).dt.days)
            E = model_data['event_occurred']

            kmf.fit(T, event_observed=E)
            km_df = kmf.survival_function_
            km_df = km_df.reset_index()
            km_df['model'] = model
            
            km_df = km_df[(km_df['timeline'] <= 180) & (km_df['timeline']>=0)]
            all_data = pd.concat([all_data, km_df])

        all_data.rename(columns={all_data.columns[1]: 'Survival_probability', 'timeline': 'Days'}, inplace=True)
        return all_data

    def style_chart(self, chart, title_text, width=600, height=300):
        chart = chart.properties(
            width=width, 
            height=height, 
            title=alt.TitleParams(title_text, fontSize=16, font=self.font, anchor='middle')
        ).configure_axis(
            labelFont=self.font,
            titleFont=self.font
        ).configure_legend(
            labelFont=self.font,
            titleFont=self.font
        )
        return chart

    def plot_data_with_tooltip(self, data, x_field, y_field, color_field, hex_palette):
        nearest = alt.selection_point(nearest=True, on='mouseover', fields=[x_field], empty='none')
        y_min = data['Survival_probability'].min()
        y_max = data['Survival_probability'].max()

        line = alt.Chart(data).mark_line(interpolate='basis').encode(
            x=alt.X(f'{x_field}:Q', scale=alt.Scale(domain=[0, 180]), title=None),
            y=alt.Y(f'{y_field}:Q', scale=alt.Scale(domain=[y_min, y_max]), title=None),
            color=alt.Color(f'{color_field}:N', scale=alt.Scale(range=hex_palette)),
            tooltip=[alt.Tooltip(f'{color_field}:N', title='Model'),
                    alt.Tooltip(f'{x_field}:Q', title='Days'),
                    alt.Tooltip(f'{y_field}:Q', title='Survival Probability')],
        ).add_params(
            nearest
        )

        selectors = alt.Chart(data).mark_point().encode(
            x=f'{x_field}:Q',
            opacity=alt.value(0),
        ).add_params(
            nearest
        )

        points = line.mark_point().encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        text = line.mark_text(align='left', dx=5, dy=-5).encode(
           text=alt.condition(nearest, f'{y_field}:Q', alt.value(' '))
        )

        rules = alt.Chart(data).mark_rule(color='gray').encode(
            x=f'{x_field}:Q',
        ).transform_filter(
            nearest
        )

        return alt.layer(line, selectors, points, rules, text)

    def plot_altair_chart(self, df, start_time_column, title_text):
        data = self.prepare_survival_data(df, start_time_column)
        unique_models = data['model'].unique()
        color_palette = sns.color_palette("dark:#5A9_r", len(unique_models))
        hex_palette = [rgb2hex(color) for color in color_palette]

        chart = self.plot_data_with_tooltip(data, 'Days', 'Survival_probability', 'model', hex_palette)
        styled_chart = self.style_chart(chart, title_text)
        st.altair_chart(styled_chart, use_container_width=True)
