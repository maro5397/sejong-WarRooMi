import requests
from bs4 import BeautifulSoup as bs
import getpass

header = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
            AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
            "Accept":"text/html,application/xhtml+xml,application/xml;\
            q=0.9,imgwebp,*/*;q=0.8"}
TIMEOUT_SEC = 3

def dosejong_api(id, pw):
    data = {
            #POST
            "email":id,
            "password":pw
            }
    with requests.Session() as s:
        html = s.post("https://do.sejong.ac.kr/ko/process/member/login", headers = header, data = data, timeout=TIMEOUT_SEC).content
        html = s.get("https://do.sejong.ac.kr/", timeout=TIMEOUT_SEC).text
        soup = bs(html, "html.parser")
        soup = soup.select("div.info")
        if soup == []: return {"result": False}
        name = soup[0].find("b").get_text().strip()
        major = soup[0].find("small").get_text().strip().split(" ")[1]
        return {
            "result":True,
            "name":name,
            "id":id,
            "major":major
        }

if __name__ == '__main__':
    id = input("학교 아이디: ")
    pw = getpass.getpass("비밀번호: ")
    print(dosejong_api(id,pw))