vaccine = [("COVAXIN","Covaxin"), ( "COVISHIELD", "Covishield"), (( "ANY", "Any"))]
fee = [("Free", "Free"), ("Paid", "Paid"), ("Any", "Any")]
dose = [("1", "1"),("2", "2")]
age = [("18", "18-44"),("45", "45+")]
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/json',
    'Origin': 'https://selfregistration.cowin.gov.in',
    'Connection': 'keep-alive',
    'Referer': 'https://selfregistration.cowin.gov.in/',
    'TE': 'Trailers',
}
stop_checking = False
partial_filter = None
txnId = None
filtered_session = None