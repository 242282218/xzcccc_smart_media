try:
    with open('test_result.log', 'r', encoding='utf-8', errors='ignore') as f:
        print(f.read())
except Exception as e:
    with open('test_result.log', 'r', encoding='gbk', errors='ignore') as f:
        print(f.read())
