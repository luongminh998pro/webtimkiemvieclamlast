from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)

# Hàm để làm sạch mức lương và chuyển đổi thành số
def clean_salary(salary_str):
    salary_str = salary_str.lower().replace('tới', '').strip()
    if '-' in salary_str:
        range_match = re.findall(r'\d+', salary_str)
        if len(range_match) == 2:
            low_salary, high_salary = range_match
            return (int(low_salary), int(high_salary))
    if '$' in salary_str:
        salary_numbers = re.findall(r'\d+', salary_str)
        if salary_numbers:
            salary = int(''.join(salary_numbers))
            return salary
    if 'triệu' in salary_str:
        salary_numbers = re.findall(r'\d+', salary_str)
        if salary_numbers:
            salary = int(''.join(salary_numbers))
            if salary == 0:
                return "thỏa thuận"
            return salary
    return salary_str

# Đọc dữ liệu từ file CSV
def get_jobs():
    df = pd.read_csv('jobs_data.csv')
    jobs = []
    
    for _, row in df.iterrows():
        title = row['Job Title']
        company = row['Company']
        salary = clean_salary(row['Salary'])
        address = row['Address']
        
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
        all_jobs.sort(key=lambda x: x['salary_str'] if isinstance(x['salary_str'], int) else (x['salary_str'][0] if isinstance(x['salary_str'], tuple) else 0))
    else:
        all_jobs.sort(key=lambda x: x['salary_str'] if isinstance(x['salary_str'], int) else (x['salary_str'][1] if isinstance(x['salary_str'], tuple) else 0), reverse=True)

    no_results = len(all_jobs) == 0

    return render_template('index.html', jobs=all_jobs, search_query=search_query, sort_order=sort_order, no_results=no_results)

if __name__ == '__main__':
    app.run(debug=True)
