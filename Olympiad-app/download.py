import requests

class download_shortlists():
    def __init__(self, url="http://imo-official.com/problems/IMO", loc=""):
        self.url=url
        self.loc=loc
    
    def retrieve(self, years):
        for year in years:
            r=requests.get(self.url+str(year)+"SL.pdf", allow_redirects=True)
            open(self.loc+str(year)+".pdf", "wb").write(r.content)