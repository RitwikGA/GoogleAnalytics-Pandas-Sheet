import pandas as pd
import pygsheets
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = 'client_secrets.json'
VIEW_ID = ''

# For the full list of dimensions & metrics, check https://developers.google.com/analytics/devguides/reporting/core/dimsmets
DIMENSIONS = ['ga:source','ga:medium']
METRICS = ['ga:users','ga:sessions']

def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(analytics):
  return analytics.reports().batchGet(
      body={
        'reportRequests': [
        {
          'viewId': VIEW_ID,
          'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
          'metrics': [{'expression':i} for i in METRICS],
          'dimensions': [{'name':j} for j in DIMENSIONS]
        }]
      }
  ).execute()


def convert_to_dataframe(response):
    
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = [i.get('name',{}) for i in columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])]
    finalRows = []
    

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      metrics = row.get('metrics', [])[0].get('values', {})
      rowObject = {}

      for header, dimension in zip(dimensionHeaders, dimensions):
        rowObject[header] = dimension
        
        
      for metricHeader, metric in zip(metricHeaders, metrics):
        rowObject[metricHeader] = metric

      finalRows.append(rowObject)
      
      
  dataFrameFormat = pd.DataFrame(finalRows)    
  return dataFrameFormat      
        
 
def export_to_sheets(df):
    gc = pygsheets.authorize(service_file='client_secrets.json')
    sht = gc.open_by_key('1nI-OAypBe4vnnW2I8IuduxpyBZMfznc7RnGFUUNLatw')
    wks = sht.worksheet_by_title('Sheet1')
    wks.set_dataframe(df,'A1')


def main():
  analytics = initialize_analyticsreporting()
  response = get_report(analytics)
  df = convert_to_dataframe(response)   #df = pandas dataframe
  export_to_sheets(df)                  #outputs to spreadsheet. comment to skip
  print(df)                             

if __name__ == '__main__':
  main()
