import argparse     # Tự động tạo help
import os           
import re           # Thư viện regex để xử lý chuỗi
import requests     # Gửi các yêu cầu HTTP
import html         # Xử lý các các ký tự trong trình duyệt
import webbrowser   # Mở các URL trong trình duyệt

# Đường dẫn đến thư mục lưu trữ các exploit
path = './exploit-db'   # "./" là thư mục hiện tại

# Lưu nội dung exploit vào tệp tin
def save_exploit(id, content):
    if not os.path.exists(path):    # Tạo thư mục nếu chưa tông tại
        os.makedirs(path)
    file_path = os.path.join(path, f'{id}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return file_path

# Tải nội dung exploit từ tệp tin nếu có.
def load_exploit(id):
    file_path = os.path.join(path, f'{id}.txt')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:   # with để đẩm bảo rằng tệp tin sẽ tự động đòng lại sau khi đọc xong, ngay cả khi có lỗi xảy ra, as là bí danh alias: có thể sử dụng bí danh 'f' để tương tác với tệp
            return f.read()
    return None

# Trích xuất ID từ URL hoặc ID trực tiếp.
def extract_id(input_str):
    # match = re.match(r'(?:https?://)?(?:www\.)?exploit-db\.com/exploits/(\d+)', input_str)
    match = re.match(r'exploit-db.com/exploits/(\d+)', input_str)   # Tiền tố r trc 1 bểu thức để đại diện cho chuỗi tiếp sau chỉ là ký tự bình thường, \d: biểu diễn là chữ số
    if match:
        return match.group(1)
    match = re.match(r'^\d+$', input_str)   # Khớp với 1 hoặc nhiều chữ số
    if match:
        return match.group(0)
    return None

# Lưu và mở file exploit 
def exploit_func(id):
    id = extract_id(id)
    if not id:
        print("Invalid exploit ID or URL.")
        return

    content = load_exploit(id)  
    if content is None:
        url = f'https://exploit-db.com/exploits/{id}'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers)    # Gửi yêu cầu HTTP GET tới URL
        if res.status_code == 200:                  # Yêu cầu thành công
            exploit = res.text[res.text.find('<code') : res.text.find('</code>')]   # Trích xuất nội dung từ thẻ <code dến </code>
            exploit = html.unescape(exploit[exploit.find('">') + 2 :])              # Giải mã các thực thể HTML (như &lt, &gt, &amp thành <, >, &)
            content = exploit
            save_exploit(id, content)   
        else:
            print(f"Failed to fetch exploit with ID {id}.")
            return

    print(f"Exploit {id} đã được lưu tại {os.path.join(path, f'{id}.txt')}. Mở tệp...") # sử dụng phương thức os.path.join() 
    
    # Mở tệp trên Windows
    os.startfile(os.path.join(path, f'{id}.txt'))

# Trả về các exploit đã lưu trữ theo page.
def page_func(page):
    try:
        page = int(page)
        files = []
        for file in os.listdir(path):
            file = int(file[:-4])
            files.append(file)
        files.sort()
        start = page * 5
        end = start + 5
        for file in files[start:end]:
            print(file)            # bỏ đuôi .txt
    except ValueError:
        print("Invalid page number.")

# Tìm kiếm từ khóa trong nội dung exploit
def search_func(keyword):
    keywords = re.split(r'\s+', keyword)    # \s: Khoảng trắng
    # \b: khớp ở đầu hoặc cuối từ, re.IGNORECASE: không phân việt chữ hoa chữ thường, (?...): Nhóm không lưu trữ, |: dấu hoặc
    regex = re.compile(r'\b(?:' + '|'.join(re.escape(word) for word in keywords) + r')\b', re.IGNORECASE)   
    files = os.listdir(path)    # trả về danh sách các tệp tin
    found = False
    for file in files:
        with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
            content = f.read()
            if regex.search(content):
                print(path,file, sep = '', end = '\n')
                found = True
    if not found:
        print("No matches found.")

if __name__ == '__main__':
    # Khởi tạo 1 argumentParser cùng với mô tả
    parser = argparse.ArgumentParser(description="Exploit-DB CLI")
    # Thêm các đối số (bên dưới là đối số tùy chọn(có "--" đằng trước), ngoài ra còn đối số vị trí(không có "--" và đối số là bắt buộc))
    parser.add_argument('--exploit', type=str, help='Lấy nội dung exploit từ exploit-db')
    parser.add_argument('--page', type=str, help='Trả về các exploit đã lưu trữ theo page')
    parser.add_argument('--search', type=str, help='Tìm kiếm từ khóa trong nội dung exploit đã lưu trữ')

    args = parser.parse_args()  # Phân tích đối số bằng phương thức parse_args()

    if args.exploit:    # Khi đối số tùy chọn --exploit đc gọi
        exploit_func(args.exploit)
    elif args.page:     # Khi đối số tùy chọn --page đc gọi
        page_func(args.page)
    elif args.search:   # Khi đối số tùy chọn --search đc gọi
        search_func(args.search)
    else:
        parser.print_help()
