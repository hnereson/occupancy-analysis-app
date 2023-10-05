import pandas as pd
import numpy as np
from lifelines import KaplanMeierFitter
import altair as alt
import seaborn as sns
from matplotlib.colors import rgb2hex
import streamlit as st

class BasePlot():
    def __init__(self):
        self.font = 'monospace'

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

    def plot_data_with_tooltip(self, data, x_field, y_field, color_field, hex_palette, x_scale, y_scale):
        nearest = alt.selection_point(nearest=True, on='mouseover', fields=[x_field], empty=False)

        line = alt.Chart(data).mark_line(interpolate='basis').encode(
            x=alt.X(f'{x_field}:Q', scale=alt.Scale(domain=x_scale), title=None),
            y=alt.Y(f'{y_field}:Q', scale=alt.Scale(domain=y_scale), title=None),
            color=alt.Color(f'{color_field}:N', scale=alt.Scale(range=hex_palette))
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

class SurvivalPlot(BasePlot):
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

        all_data.rename(columns={all_data.columns[1]: '% Survived', 'timeline': 'Days'}, inplace=True)
        all_data['% Survived'] = all_data['% Survived'].round(3)
        return all_data

    def plot_altair_chart(self, df, start_time_column, title_text):
        data = self.prepare_survival_data(df, start_time_column)
        unique_models = data['model'].unique()
        color_palette = sns.color_palette("dark:#5A9_r", len(unique_models))
        hex_palette = [rgb2hex(color) for color in color_palette]
        y_min = data['% Survived'].min()
        x_max = min(180, data['Days'].max())

        chart = self.plot_data_with_tooltip(data, 'Days', '% Survived', 'model', hex_palette, x_scale=[0, x_max], y_scale=[y_min, 1])
        styled_chart = self.style_chart(chart, title_text)
        st.altair_chart(styled_chart, use_container_width=True)

class HeatmapPlot(BasePlot):
    def __init__(self):
        super().__init__()
    
    def prepare_heatmap_data(self, heatmap_data):
        # Reset index for the heatmap data
        data = heatmap_data.reset_index().melt(id_vars='year', value_name='% moved out', var_name='month')
        return data
    
    def plot_altair_heatmap(self, data, x_field, y_field, color_field, title_text, color_palette="teals"):
        """
        Create a heatmap using Altair based on the provided data.

        Parameters:
        - data (pd.DataFrame): Data for the heatmap.
        - x_field (str): Field to be used for the x-axis.
        - y_field (str): Field to be used for the y-axis.
        - color_field (str): Field to determine the color of the heatmap cells.
        - title_text (str): Title for the heatmap.
        - color_scheme (str, optional): Color scheme for the heatmap. Defaults to 'teals'.

        Returns:
        - chart: Altair heatmap chart.
        """
        # Define the heatmap chart
        chart = alt.Chart(data).mark_rect().encode(
            x=alt.X(f'{x_field}:O', title=''),
            y=alt.Y(f'{y_field}:O', title=''),
            color=alt.Color(f'{color_field}:Q', scale=alt.Scale(scheme=color_palette)),
            tooltip=[x_field, y_field, color_field]
        )

        # Style the chart
        styled_chart = self.style_chart(chart, title_text, width=600, height=400)
        return styled_chart

    def display_heatmap(self, data, x_field, y_field, color_field, title_text):
        """
        Display the heatmap using Streamlit.

        Parameters:
        - data (pd.DataFrame): Data for the heatmap.
        - x_field (str): Field to be used for the x-axis.
        - y_field (str): Field to be used for the y-axis.
        - color_field (str): Field to determine the color of the heatmap cells.
        - title_text (str): Title for the heatmap.
        """
        # Create a palette that starts from a light teal (close to white) and progresses to a dark teal

        data = self.prepare_heatmap_data(data)
        heatmap = self.plot_altair_heatmap(data, x_field, y_field, color_field, title_text)
        st.altair_chart(heatmap, use_container_width=True)

class HistogramPlot(BasePlot):
    def __init__(self):
        super().__init__()
    
    def prepare_histogram_data(self, move_out_df, start_date, end_date):
        """
        Prepare data for the histogram based on the provided date range.
        
        Parameters:
        - move_out_df (pd.DataFrame): DataFrame with move-out data.
        - start_date (datetime): Start date for the desired range.
        - end_date (datetime): End date for the desired range.
        
        Returns:
        - sorted_df (pd.DataFrame): DataFrame with Y/Y change prepared for histogram plotting.
        """
        move_out_df['date'] = move_out_df['date'].dt.date

        # Now filter based on the date range
        current_year_data = move_out_df[(move_out_df['date'] >= start_date) & (move_out_df['date'] <= end_date)]
        previous_year_data = move_out_df[(move_out_df['date'] >= (start_date - pd.DateOffset(years=1)).date()) & (move_out_df['date'] <= (end_date - pd.DateOffset(years=1)).date())]

        # Merge the two dataframes on 'site_code' to calculate the Y/Y change
        merged_df = current_year_data[['site_code', '% moved out']].merge(previous_year_data[['site_code', '% moved out']], on='site_code', suffixes=('_current', '_prev'))

        # Calculate the Y/Y change
        merged_df['yoy_change'] = merged_df['% moved out_current'] - merged_df['% moved out_prev']

        merged_df = merged_df[~merged_df['yoy_change'].isna()]
        # Sort the dataframe by 'yoy_change'
        sorted_df = merged_df.sort_values(by='yoy_change', ascending=False)

        return sorted_df

    def plot_altair_histogram(self, data, x_field, title_text, x_title, y_title, bar_color="teal", num_bins=30, bar_width=15, density=False):
        """
        Create a histogram using Altair based on the provided data.
        
        Parameters:
        - data (pd.DataFrame): Data for the histogram.
        - x_field (str): Field to be used for the x-axis.
        - title_text (str): Title for the histogram.
        - color_palette (str, optional): Color palette for the histogram. Defaults to None.
        
        Returns:
        - chart: Altair histogram chart.
        """
        min_value = data[x_field].min()
        max_value = data[x_field].max()
        bin_edges = np.linspace(min_value, max_value, num_bins + 1)

        # Assign each data point to a bin
        data['bin'] = np.digitize(data[x_field], bin_edges, right=True) - 1

        # Group by the bin and count the number of data points in each bin
        binned_data = data.groupby('bin').size().reset_index(name='count')
        binned_data[x_field] = (bin_edges[binned_data['bin']] + bin_edges[binned_data['bin'] + 1]) / 2

        # Plot the histogram using Altair
        chart = alt.Chart(binned_data).mark_bar(color=bar_color, size=bar_width).encode(
            x=alt.X(f'{x_field}:Q', title=x_title, axis=alt.Axis(grid=False)),
            y=alt.Y('count:Q', title=y_title, axis=alt.Axis(grid=False)),
            tooltip=[x_field, 'count']
        )
        # Density plot (like KDE)
        max_count = binned_data['count'].max()
        if density == True:
            density = alt.Chart(data).transform_density(
                density=x_field,
                as_=[x_field, 'density'],
                bandwidth=0.5  # Adjust bandwidth as needed
            ).transform_calculate(
                scaled_density=f'datum.density * {max_count}'  # Rescale density values
            ).mark_line(color='red').encode(
                x=f'{x_field}:Q',
                y=alt.Y('scaled_density:Q', axis=alt.Axis(grid=False))
            )

            chart = (chart + density)
        
        chart = chart.interactive()
        # Style the chart
        styled_chart = self.style_chart(chart, title_text, width=600, height=400)
        st.altair_chart(styled_chart, use_container_width=True)


class ScatterPlot(BasePlot):
    def __init__(self):
        super().__init__()

    def prepare_scatter_data(self, data, pred_moveouts_df, end_date):
        """
        Prepare data for the scatterplot based on the provided end date.
        
        Parameters:
        - move_out_df (pd.DataFrame): DataFrame with move-out data.
        - pred_moveouts_df (pd.DataFrame): DataFrame with predicted move-outs.
        - end_date (datetime): End date for the desired range.
        
        Returns:
        - merged_scatter_data (pd.DataFrame): DataFrame prepared for scatter plotting.
        """
        
        # Filter move_out_df for the given end_date
        filtered_data = data[data['date'] == end_date]

        # Merge the filtered data with predicted move-outs
        merged_scatter_data = filtered_data[['site_code', '% moved out', 'move_outs']].merge(pred_moveouts_df, on='site_code')
        merged_scatter_data['percentage_difference'] = 100 * (merged_scatter_data['move_outs'] - merged_scatter_data['predicted_moveouts']) / merged_scatter_data['predicted_moveouts']

        return merged_scatter_data

    def plot_altair_scatterplot(self, data, x_field, y_field, title_text, color_palette="teals"):
        """
        Create a scatterplot using Altair based on the provided data.
        
        Parameters:
        - data (pd.DataFrame): Data for the scatterplot.
        - x_field (str): Field to be used for the x-axis.
        - y_field (str): Field to be used for the y-axis.
        - title_text (str): Title for the scatterplot.
        - color_palette (str, optional): Color palette for the scatterplot. Defaults to None.
        
        Returns:
        - chart: Altair scatterplot chart.
        """
        # Define the scatterplot chart
        chart = alt.Chart(data).mark_circle().encode(
            x=alt.X(f'{x_field}:Q', title='% Moved Out (Sep 2023)'),
            y=alt.Y(f'{y_field}:Q', title='% Difference (Actual - Pred) / Pred'),
            color=alt.Color(scale=alt.Scale(scheme=color_palette)),
            tooltip=[x_field, y_field]
        )

        # Style the chart
        styled_chart = self.style_chart(chart, title_text, width=600, height=400)
        st.altair_chart(styled_chart, use_container_width=True)
