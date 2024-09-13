from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Hàm để làm sạch mức lương
def clean_salary(salary_str):
    salary_str = salary_str.lower().replace('tới', '').strip()
    if '-' in salary_str:
        range_match = re.findall(r'\d+', salary_str)
        if len(range_match) == 2:
            low_salary, high_salary = range_match
            return f"{low_salary} - {high_salary} triệu VND"
    if '$' in salary_str:
        salary_numbers = re.findall(r'\d+', salary_str)
        if salary_numbers:
            salary = int(''.join(salary_numbers))
            return f"{salary} USD"
    if 'triệu' in salary_str:
        salary_numbers = re.findall(r'\d+', salary_str)
        if salary_numbers:
            salary = int(''.join(salary_numbers))
            if salary == 0:
                return "thỏa thuận"
            return f"{salary} triệu VND"
    return salary_str

# URL của các trang cần crawl
urls = [
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&sba=1",
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&page=2&sba=1",
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&page=3&sba=1",
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&page=4&sba=1",
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&page=5&sba=1",
    "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-c10131?type_keyword=1&page=6&sba=1",

]

# Hàm để lấy dữ liệu công việc từ các trang
def get_jobs():
    jobs = []
    for url in urls:
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')

        # Tìm các phần tử công việc
        job_listings = soup.find_all('div', class_='job-item-search-result')

        for listing in job_listings:
            title_element = listing.find('h3', class_='title')
            company_element = listing.find('a', class_='company')
            salary_element = listing.find('label', class_='title-salary')
            address_element = listing.find('label', class_='address')

            title = title_element.get_text(strip=True) if title_element else "N/A"
            company = company_element.get_text(strip=True) if company_element else "N/A"
            salary = clean_salary(salary_element.get_text(strip=True)) if salary_element else "N/A"
            address = address_element.get_text(strip=True) if address_element else "N/A"

            jobs.append({
                'title': title,
                'company': company,
                'salary_str': salary,
                'address': address
            })
    return jobs

@app.route('/', methods=['GET', 'POST'])
def index():
    search_query = request.form.get('search_query', '')
    sort_order = request.form.get('sort_order', 'desc')
    
    all_jobs = get_jobs()  # Lấy danh sách công việc

    # Tìm kiếm công việc
    if search_query:
        all_jobs = [job for job in all_jobs if search_query.lower() in job['title'].lower() or search_query.lower() in job['company'].lower()]

    # Sắp xếp theo mức lương
    if sort_order == 'asc':
        all_jobs.sort(key=lambda x: x['salary_str'], reverse=False)
    else:
        all_jobs.sort(key=lambda x: x['salary_str'], reverse=True)

    no_results = len(all_jobs) == 0

    return render_template('index.html', jobs=all_jobs, search_query=search_query, sort_order=sort_order, no_results=no_results)

if __name__ == '__main__':
    app.run(debug=True)
