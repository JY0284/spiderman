# housing_trade_module.py

import os
import logging
import sqlite3
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment
from db.db import DBHandler

matplotlib.use('Agg')  # Use a non-interactive backend

class HousingTradeAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Database operations
    def fetch_data_from_db(self, db_path, query):
        """Fetch data from SQLite database."""
        self.logger.info("Fetching data from database.")
        conn = sqlite3.connect(db_path)
        try:
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()
        return df

    # Data preprocessing
    def preprocess_data(self, df):
        """Preprocess data, handle missing values, and convert data types."""
        self.logger.info("Preprocessing data.")
        listing_columns = ['listing_all', 'listing_agency', 'listing_person', 'deal_cnt']
        df['deal_cnt'] = df['deal_cnt'].apply(lambda x: x if x else 0)
        df[listing_columns] = df[listing_columns].fillna(0).astype(int)
        df['date'] = pd.to_datetime(df['date'])
        #TODO duplicate handling
        df = df.sort_values('date')
        return df

    # Visualization
    def plot_data(self, df, output_path):
        """Generate and save a plot for listings and deal counts over time."""
        self.logger.info("Generating plot.")
        sns.set_theme(style="whitegrid")

        # Initialize the plot
        fig, ax1 = plt.subplots(figsize=(14, 7))
        palette = sns.color_palette("husl", 2)
        color_listing = palette[1]
        color_deal = palette[0]

        # Bar chart for 'listing_all'
        ax1.bar(df['date'], df['listing_all'], color=color_listing, label='Total Listings')
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Total Listings', color=color_listing, fontsize=12)
        ax1.tick_params(axis='y', labelcolor=color_listing, labelsize=10)

        # Calculate and set y-axis limits dynamically
        data_min = df['listing_all'].min()
        data_max = df['listing_all'].max()
        ax1.set_ylim(max(data_min, 149000), data_max * 1.01)
        ax1.yaxis.grid(True, which='major', linestyle='--', linewidth=0.5)

        # Line plot for 'deal_cnt'
        ax2 = ax1.twinx()
        ax2.plot(df['date'], df['deal_cnt'], color=color_deal, marker='o', label='Deal Count')
        ax2.set_ylabel('Deal Count', color=color_deal, fontsize=12)
        ax2.tick_params(axis='y', labelcolor=color_deal, labelsize=10)
        ax2.yaxis.grid(True, which='major', linestyle='--', linewidth=0.5)

        # Combine legends
        lines_labels = [ax.get_legend_handles_labels() for ax in [ax1, ax2]]
        handles, labels = [sum(lol, []) for lol in zip(*lines_labels)]
        ax1.legend(handles, labels, loc='upper left', fontsize=10)

        # Finalize formatting
        fig.suptitle('Total Listings and Deal Count Over Time', fontsize=16)
        fig.autofmt_xdate(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        self.logger.info(f"Plot saved to {output_path}.")

    # HTML generation
    def generate_html_table(self, df, output_path):
        """Generate an HTML table from the data."""
        self.logger.info("Generating HTML table.")
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-family: Arial, sans-serif;
                }
                th, td {
                    border: 1px solid #dddddd;
                    text-align: center;
                    padding: 8px;
                }
                th {
                    background-color: #f2f2f2;
                }
                tr:nth-child(even) {
                    background-color: #fafafa;
                }
            </style>
        </head>
        <body>
            <h2>最近30日二手房成交明细</h2>
            <table>
                <thead>
                    <tr>
                        {% for column in columns %}
                        <th>{{ column }}</th>
                        {% endfor %}
                    </tr>
                </thead>
                <tbody>
                    {% for row in data %}
                    <tr>
                        {% for item in row %}
                        <td>{{ item }}</td>
                        {% endfor %}
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </body>
        </html>
        """
        env = Environment()
        template = env.from_string(html_template)
        columns = df.columns.tolist()
        data = df.values.tolist()[-30:][::-1]
        html_content = template.render(columns=columns, data=data)

        with open(output_path, 'w') as f:
            f.write(html_content)
        self.logger.info(f"HTML table saved to {output_path}.")

    # Public function
    def process_housing_data(self, db_handler, plot_output_path='listing_deal_plot.png', html_output_path='housing_trade_info_table.html'):
        """Orchestrates data processing, visualization, and HTML generation.

        Args:
            db_path (str): Path to the SQLite database.
            query (str): SQL query to fetch data.
            plot_output_path (str): File path for saving the plot. Defaults to 'listing_deal_plot.png'.
            html_output_path (str): File path for saving the HTML table. Defaults to 'housing_trade_info_table.html'.

        Returns:
            dict: Dictionary containing paths of the generated files.
        """
        self.logger.info("Starting data processing workflow.")

        plot_output_path = os.path.join(os.path.dirname(__file__), plot_output_path)
        html_output_path = os.path.join(os.path.dirname(__file__), html_output_path)

        # Step 1: Data fetching and preprocessing
        query = "SELECT * FROM nj_existing_housing_trade_info_collector"
        df = self.fetch_data_from_db(db_handler.absolute_db_path(), query)
        df = self.preprocess_data(df)

        # Step 2: Generate plot
        self.plot_data(df, plot_output_path)

        # Step 3: Generate HTML table
        self.generate_html_table(df, html_output_path)

        self.logger.info("Data processing workflow completed.")
        return {
            'plot': plot_output_path,
            'table': html_output_path
        }

if __name__ == "__main__":
    module = HousingTradeAnalysis()
    db_handler = DBHandler(os.path.join(os.path.dirname(__file__), "..", "db", "data.db"))
    print(db_handler.db_path)
    output_files = module.process_housing_data(db_handler)
    module.logger.info(f"Generated files: {output_files}")
