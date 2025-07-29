import requests
from bs4 import BeautifulSoup

def get_latest_blog_url(base_url):
    res = requests.get(base_url)
    soup = BeautifulSoup(res.text, "html.parser")
    first_post = soup.select_one("a[href^='/blog/detail/']")
    if not first_post:
        return None
    post_url = first_post["href"]
    return "https://bokuao.com" + post_url

def parse_blog_detail(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    writer = soup.find("p", class_="writer").text.strip()
    title = soup.find("p", class_="tit").text.strip()
    date = soup.find("p", class_="date").text.strip()
    images = [img["src"] for img in soup.select("div.txt img") if img.get("src", "").startswith("http")]

    return {
        "writer": writer,
        "title": title,
        "images": images,
        "url": url,
        "date": date
    }
