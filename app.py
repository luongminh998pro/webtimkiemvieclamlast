from flask import Flask, render_template, request
import csv
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

# Đọc dữ liệu từ file CSV
def get_jobs():
    jobs = []
    with open('jobs_data.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            title = row.get('Job Title', 'N/A')
            company = row.get('Company', 'N/A')
            salary = clean_salary(row.get('Salary', 'N/A'))
            address = row.get('Address', 'N/A')
            
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
