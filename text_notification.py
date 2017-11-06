from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SheetReader:
  def __init__(self, scope, client_secret, url):
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    self.client = authorize(creds)
    self.url = url
    self.row_timestamp = "Timestamp"
    self.row_phone_num = "Phone Number"
    self.row_carrier = "Carrier"
    self.row_unlisted_carrier = "Unlisted Carrier"
    self.row_domain = "Domain"
    self.carrier_dic = self._getCarrierDic()

  #pulls symbol map of carriers to their domain in gsheet
  def _getCarrierDic(self):
    index = 1
    raw_data = self.getSheetByIndex(index)
    #index for data from symbol_map

    carrier_dic = dict()
    for line in raw_data:
      carrier_dic[line[self.row_carrier]] = line[self.row_domain]
    return carrier_dic

  def getSheetByIndex(self, i):
    return self.client.open_by_url(self.url).get_worksheet(i).get_all_records()

  def run(self):
    index = 0
    raw_data = self.getSheetByIndex(0)
    #index for data from google form (phone & carrier)

    ans_str = ""
    for line in raw_data:
      if self._rowNonEmpty(line) and self._isToday(line):
        ans_str += self._transformRawLine(line)
    return ans_str.rstrip()

  #check if row of data input is considered nonempty
  def _rowNonEmpty(self, line):
    return line[self.row_timestamp]
    #checks to see if timestamp field exists

  #transfrom data input into number@carrierdomain;
  def _transformRawLine(self, line):
    return "{0}{1};\n".format(
      line[self.row_phone_num],
      self._getCarrierDomain(line)
      )

  #check if timestamp in line is same as today
  def _isToday(self, line):
    line = datetime.strptime(line[self.row_timestamp].split()[0], '%m/%d/%Y').date()
    today = datetime.today().date()
    #take only date portion of timestamp

    return line == today

  #attempts to map carrier to its domain
  def _getCarrierDomain(self, line):
    unlisted = line[self.row_unlisted_carrier]
    if not unlisted: #if not empty
      return self.carrier_dic[line[self.row_carrier]]
    else:
      return "@{0}[unlisted domain]".format(unlisted)

if __name__ == '__main__':
  scope = ["https://spreadsheets.google.com/feeds"]
  client_secret = "client_secret.json"
  url = "https://docs.google.com/spreadsheets/d/1lbWSb7C84LwZIfGzS8GwJiJ6SBKBTaxHwjvFoQjOxvU"

  my_sheet = SheetReader(scope, client_secret, url)
  print(my_sheet.run())