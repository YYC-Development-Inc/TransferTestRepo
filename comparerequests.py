import json
from deepdiff import DeepDiff
import argparse
import os

def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_to_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def format_json_content(content):
    try:
        # Attempt to parse the content as JSON and return a pretty-printed version
        return json.dumps(json.loads(content), indent=4)
    except json.JSONDecodeError:
        # Return the original content if it's not valid JSON
        return content

def find_first_difference(str1, str2):
    """Find the index at which two strings first differ."""
    min_len = min(len(str1), len(str2))
    backslash_count = 0;
    title_length = len("        \"response_content\": \"");

    for i in range(min_len):
        if str1[i] == "\\" or str1[i] == "\"":
            backslash_count += 1

        if str1[i] != str2[i]:
            return i + backslash_count + title_length + 1

    if len(str1) != len(str2):
        return min_len  # This accounts for one string being a substring of the other
    return -1  # Strings are identical

# Sorting function
def sort_lists_by_id(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = sort_lists_by_id(value)
    elif isinstance(obj, list):
        obj = sorted(obj, key=lambda x: x.get('id', 0)) if all(isinstance(i, dict) for i in obj) else obj
        obj = [sort_lists_by_id(item) for item in obj]
    return obj

def compare_files(file1_path, file2_path, output_dir='./output'):
    data1 = load_data(file1_path)
    data2 = load_data(file2_path)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    data2_dict = {(d['parameters'], d['request_payload']): d for d in data2}

    matched, unmatched, unmatched_differences, unmatched_responseonly, unmatched_responseonly_formatted, unique_to_file1 = [], [], [], [], [], []

    for request1 in data1:
        key = (request1['parameters'], request1['request_payload'])
        request2 = data2_dict.get(key)

        if request2:
            if request1['response_content'] == request2['response_content']:
                matched.append(request1)
            else:
                diff_index = find_first_difference(request1['response_content'], request2['response_content'])

                #print(f"DEBUG: response_content: {request1['response_content']}")

                # Format the JSON content for better diff comparison
                #request1['request_payload'] = format_json_content(request1['request_payload'])
                #request1['response_content'] = format_json_content(request1['response_content'])
                #request2['request_payload'] = format_json_content(request2['request_payload'])
                #request2['response_content'] = format_json_content(request2['response_content'])
                request1_responseonly ={
                    'request_payload': request1['request_payload'],
                    'response_content': request1['response_content']
                }

                request2_responseonly ={
                    'request_payload': request2['request_payload'],
                    'response_content': request2['response_content']
                }

                unmatched.append({'file1': request1, 'file2': request2})
                unmatched_responseonly.append({'file1': request1_responseonly, 'file2': request2_responseonly})

                json_request1 = json.loads(request1['response_content'])
                json_request2 = json.loads(request2['response_content'])

                json_request1_sorted = sort_lists_by_id(json_request1)
                json_request2_sorted = sort_lists_by_id(json_request2)

                #print(f"DEBUG: response_content: {json_request1_sorted}")
                # Compare
                diff = DeepDiff(json_request1_sorted, json_request2_sorted, ignore_order=True)
                print(diff)


                unmatched_responseonly_formatted.append({
                    'file1': json_request1_sorted,
                    'file2': json_request2_sorted,
                })   
                

                unmatched_differences.append({
                    'request_payload': request1['request_payload'],
                    'difference_index': diff_index,
                    'file1_content_length': len(request1['response_content']),
                    'file2_content_length': len(request2['response_content']),
                })                
            del data2_dict[key]
        else:
            unique_to_file1.append(request1)

    unique_to_file2 = list(data2_dict.values())

    # Prepare data for unmatched responses from both files
    unmatched_file1 = [um['file1'] for um in unmatched_responseonly]
    unmatched_file2 = [um['file2'] for um in unmatched_responseonly]
    unmatched_formatted_file1 = [um['file1'] for um in unmatched_responseonly_formatted]
    unmatched_formatted_file2 = [um['file2'] for um in unmatched_responseonly_formatted]



    print(f"Matched Requests/Responses: {len(matched)}")
    print(f"Unmatched Requests/Responses: {len(unmatched)}")
    print(f"Unique to {file1_path}: {len(unique_to_file1)}")
    print(f"Unique to {file2_path}: {len(unique_to_file2)}")

    #print("unmatched_responseonly_formatted:")
    #print(unmatched_responseonly_formatted)

    unmatched_file_path = os.path.join(output_dir, 'unmatched_responses.json')
    unmatched_diffs_path = os.path.join(output_dir, 'unmatched_differences.json')

    unmatched_file1_path = os.path.join(output_dir, f"unmatched_responses_{os.path.basename(file1_path)}")
    unmatched_file2_path = os.path.join(output_dir, f"unmatched_responses_{os.path.basename(file2_path)}")

    unmatched_formatted_file1_path = os.path.join(output_dir, f"unmatched_responsesonly_formatted_{os.path.basename(file1_path)}")
    unmatched_formatted_file2_path = os.path.join(output_dir, f"unmatched_responsesonly_formatted_{os.path.basename(file2_path)}")

    unique_file1_path = os.path.join(output_dir, f"unique_to_{os.path.basename(file1_path)}")
    unique_file2_path = os.path.join(output_dir, f"unique_to_{os.path.basename(file2_path)}")

    save_to_file(unmatched, unmatched_file_path)
    save_to_file(unmatched_differences, unmatched_diffs_path)
    save_to_file(unmatched_file1, unmatched_file1_path)
    save_to_file(unmatched_file2, unmatched_file2_path)
    save_to_file(unmatched_formatted_file1, unmatched_formatted_file1_path)
    save_to_file(unmatched_formatted_file2, unmatched_formatted_file2_path)


    save_to_file(unique_to_file1, unique_file1_path)
    save_to_file(unique_to_file2, unique_file2_path)

    print(f"Details of unmatched responses saved to: {unmatched_file_path}")
    print(f"Differences in unmatched responses saved to: {unmatched_diffs_path}")
    print(f"Requests unique to {file1_path} saved to: {unique_file1_path}")
    print(f"Requests unique to {file2_path} saved to: {unique_file2_path}")
    print(f"Unmatched responses from {file1_path} saved to: {unmatched_file1_path}")
    print(f"Unmatched responses from {file2_path} saved to: {unmatched_file2_path}")    

def main():
    parser = argparse.ArgumentParser(description="Compares two JSON files for matched, unmatched, and unique requests/responses.")
    parser.add_argument('file1_path', type=str, help="Path to the first output JSON file.")
    parser.add_argument('file2_path', type=str, help="Path to the second output JSON file.")

    args = parser.parse_args()

    compare_files(args.file1_path, args.file2_path)

if __name__ == "__main__":
    main()
