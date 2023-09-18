def extract_section(start_keyword, end_keyword, lines):
    data = []
    start_index = -1
    for i, line in enumerate(lines):
        if start_keyword in line:
            start_index = i
        if start_index != -1 and end_keyword in line:
            data.append(line)
            if line == end_keyword:
                break
    return data[1:-1]  # Exclude start and end keywords