# scheduler/scheduler.py

import schedule
import time
import threading
from collectors import load_collectors, Collector
from notifier.emial_notifier import EmailNotifier
from config.config import config
import logging

from analysis.house_trade import HousingTradeAnalysis


# TODO think about pros and cons of cronjob substitution

def run_threaded(job_func, *args):
    """
    Run a job in a separate thread, passing arguments to the job function.
    """
    job_thread = threading.Thread(target=job_func, args=args)
    job_thread.start()

def run_collector(collector: Collector):
    """
    Run a single collector: collect, process, store, and notify.
    Args:
        collector: An instance of a Collector subclass.
    """
    logger = logging.getLogger(collector.__class__.__name__)
    logger.info("Starting collector run.")
    try:
        raw_data = collector.collect()
        if not raw_data:
            logger.warning("No data collected.")
            return

        processed_data = collector.process_data(raw_data)
        if not processed_data:
            logger.warning("No data processed.")
            return

        logger.info(processed_data)

        # Insert into the collector's specific table
        collector.insert_data(processed_data)
        logger.info(f"Data inserted into table '{collector.table_name}'.")

        res_paths = HousingTradeAnalysis().process_housing_data(collector.db_handler)

        # Initialize notifier
        notifier = EmailNotifier(config)
        # Fetch user emails from the database
        recipients = collector.db_handler.get_user_emails()
        # recipients = None
        if not recipients:
            # Use default recipient if no user preferences
            recipients = [('admin', config['Notifier']['default_recipient'])]
            logger.info("No user preferences found. Using default recipient.")

        # Prepare email content
        subject = f"[beta]数据更新通知/Data Notification: {collector.__class__.__name__}"

        # TODO collector -> data -> analyzer -> result -> message builder -> msg -> notifier -> email
        # Start with an introductory header and notice
        body = """
        <html>
            <body>
                <h2>最新数据/Here is the latest data:</h2>
                
                <!-- Add a styled notice section -->
                <div style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px;">
                    <p style="margin: 0; font-size: 14px; line-height: 1.6;">
                        <strong>Notice:</strong> 数据采集时间的所有挂牌数据为截止到采集时间的实时数据，昨日成交数据为截止到采集时间的“昨日”。<br>
                        目前为二手房数据，官方数据来源。后面将陆续加入其他主要城市数据及成交价格数据（正在收集可靠数据源）。
                    </p>
                </div>
                
                <!-- Data table -->
                <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%; text-align: left;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="padding: 8px;">Key</th>
                            <th style="padding: 8px;">Value</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        # Populate the table rows
        for key, value in processed_data.items():
            body += f"""
                        <tr>
                            <td style="padding: 8px;">{key}</td>
                            <td style="padding: 8px;">{value}</td>
                        </tr>
            """

        # Close the table and HTML tags
        body += """
                    </tbody>
                </table>
            </body>
        </html>
        """

        # input(recipients)

        for _, email in recipients:
            try:
                notifier.send_email(subject, body, email, res_paths["plot"], res_paths["table"])
                logger.info(f"Notification sent to {email}.")
            except Exception as e:
                logger.error("Failed to send email: " + e)

    except Exception as e:
        logger.error(f"Error during collector run: {e}")

    logger.info(f"Collector {collector.name} run finished.")

def schedule_collectors(collectors):
    """
    Schedule each collector based on its individual schedule configuration.
    Args:
        collectors: A list of Collector instances.
    """
    logger = logging.getLogger('Scheduler')
    for collector in collectors:
        interval = collector.schedule_interval.lower()
        time_str = collector.schedule_time
        if interval == 'daily':
            schedule.every().day.at(time_str).do(run_threaded, run_collector, collector)
            logger.info(f"Scheduled '{collector.__class__.__name__}' daily at {time_str}.")
        elif interval == 'hourly':
            minute = time_str.split(':')[1]  # e.g., '30' from '00:30'
            schedule.every().hour.at(f":{minute}").do(run_threaded, run_collector, collector)
            logger.info(f"Scheduled '{collector.__class__.__name__}' hourly at minute {minute}.")
        else:
            logger.warning(f"Unknown schedule interval '{interval}' for collector '{collector.__class__.__name__}'.")

def main():
    logger = logging.getLogger('Scheduler')
    # Load all collectors dynamically
    collectors = load_collectors(config)
    schedule_collectors(collectors)
    logger.info("Scheduler started.")

    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second

if __name__ == "__main__":
    main()
    # run_collector(load_collectors(config)[0]) # TODO will be an 'official' test case
