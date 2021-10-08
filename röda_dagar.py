"""A script to produce an ics file containing red days in Sweden.

The class RödaDagar contains methods to retrieve red days in Sweden for
specified years and save an ics file containing all these days as 
all-day event. Red days are available for years between 1900 and 2100. 
There is an option to exclude red days which fall on the weekend.
"""

from ast import literal_eval
import time

import pandas as pd


class RödaDagar:
    """Class to create an ics file containing red days in Sweden.
    
    Arguments
        years - list of years for which red days are retrieved.
        weekends - boolean specifiying if red days falling on weekends 
            are included.
    """
    def __init__(self, years, weekends):
        self.years = years
        self.weekends = weekends
    
    def download_dates(self):
        """Download red day data for each specified year.
        
        Returns
            Data Frame containing information on red days for all years.
        """
        url = 'https://www.kalender.se/helgdagar/'
        df = pd.DataFrame()

        for year in self.years:
            year_url = url + str(year)
            table = pd.read_html(year_url)[0]
            df = df.append(table)
            time.sleep(5)
        
        return df
    
    def format_dates(self):
        """Format dates for ics file.
        
        If weekends are to be excluded, drop them from the Data 
        Frame. To get an 'all-day' event in an ics file, the end date 
        needs to be set as the day after the event date. Therefore, the 
        date column is converted to datetime format so a day can be 
        added to each date. Each start and end date is then converted to
        the required format which is yyyymmdd.
        
        Returns
            Data Frame with formatted dates.
        """
        df = self.download_dates()
        
        if not self.weekends:
            df = df[~df['Veckodag'].isin(['Lördag', 'Söndag'])]
        
        df['Datum'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')
        df['date_start'] = df['Datum'].astype(str).replace('-', '', regex=True)
        df['date_end'] = ((df['Datum'] + pd.Timedelta('1d'))
                          .astype(str).replace('-', '', regex=True)
                         )
        return df
        
    def create_ics(self):
        """Save red days as events in ics file.
        
        For each day, the event template is filled with that day's
        information and appended to a list. This list is then joined 
        into a single string where it is inserted into the calendar
        template. This string is then saved as an ics file.
        """
        calendar_template = ("BEGIN:VCALENDAR\n"
                             "VERSION:2.0\n"
                             "{}"
                             "END:VCALENDAR")

        event_template = ("BEGIN:VEVENT\n"
                          "DTSTART:{}\n"
                          "DTEND:{}\n"
                          "SUMMARY:{}\n"
                          "END:VEVENT\n")
        
        df = self.format_dates()
        start_dates = list(df['date_start'])
        end_dates = list(df['date_end'])
        summaries = list(df['Namn'])

        events = []

        for start, end, summary in zip(start_dates, end_dates, summaries):
            events.append(event_template.format(start, end, summary))
            
        events = "".join(events)

        with open('röda_dagar.ics', 'w') as file:
            file.write(calendar_template.format(events))
            

if __name__ == "__main__":
    years = [int(year) 
             for year in input("Years (separate with commas): ").split(',')]
    weekends = literal_eval(input("Include Weekends (True/False): "))
    
    holiday = RödaDagar(years, weekends)
    holiday.create_ics()