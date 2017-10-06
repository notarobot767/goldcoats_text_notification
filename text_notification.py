import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetReader:
  def __init__(self, scope, client_secret, url):
    creds = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)
    self.client = gspread.authorize(creds)
    self.url = url
    self.carrier_dic = self.getCarrierDic()

  def getSheetByIndex(self, i):
    return self.client.open_by_url(self.url).get_worksheet(i).get_all_records()

  def getPhoneEmailString(self):
    raw_data = self.getSheetByIndex(0) #data from google form (phone & carrier)
    phone_string = ""
    for line in raw_data:
      if not self._isPhoneEmpty(line):
        phone_string += self.getFormattedPhone(line)
    return phone_string.rstrip("\n")

  def _isPhoneEmpty(self, line):
    return not line["phone_number"]

  def getCarrierDic(self):
    raw_data = self.getSheetByIndex(1) #data from symbol_map
    carrier_dic = dict()
    for line in raw_data:
      carrier_dic[line["carrier"]] = line["domain"]
    return carrier_dic

  def getCarrierDomain(self, line_phone_data):
    unlisted = line_phone_data["unlisted_carrier"]
    if not unlisted: #if not empty
      return self.carrier_dic[line_phone_data["carrier"]]
    else:
      return "@" + unlisted + "[unlisted domain]"

  def getPhoneNumber(self, line_phone_data):
    return line_phone_data["phone_number"]

  def getFormattedPhone(self, line_phone_data):
    return "{0}{1};\n".format(
      self.getPhoneNumber(line_phone_data),
      self.getCarrierDomain(line_phone_data)
      )

if __name__ == '__main__':
  scope = ["https://spreadsheets.google.com/feeds"]
  client_secret = "client_secret.json"
  url = "https://docs.google.com/spreadsheets/d/1lbWSb7C84LwZIfGzS8GwJiJ6SBKBTaxHwjvFoQjOxvU"

  my_sheet = SheetReader(scope, client_secret, url)
  print(my_sheet.getPhoneEmailString())
