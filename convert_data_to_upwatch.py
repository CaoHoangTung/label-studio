import os
import pandas as pd
import json

path = 'C:\\Users\\ADMIN\\AppData\\Local\\label-studio\\label-studio\\export\\project-1-at-2023-06-24-12-02-5b4f28b2.json'

def get_filename(annotation_item):
    annotation_id = annotation_item['id']
    annotation_file_upload = annotation_item['file_upload']
    return f"export-{annotation_id}-{annotation_file_upload}.csv"

def process_annotation(annotation_item, output_dir):
    export_filename = get_filename(annotation_item)

    sensor_offset = annotation_item['data']['sensor_offset']
    csv_path = annotation_item['data']['csv_path']

    signal_data = pd.read_csv(csv_path)

    # Calculate the ax3 array from its components
    signal_data['ax3_butterworth'] = signal_data[[f'ax3_{idx}' for idx in range(5)]].apply(lambda row: row.values.tolist(), axis=1)

    with open(export_filename, 'w') as fout:
        # Only using first user annotation
        annotation_result = annotation_item['annotations'][0]['result']

        events, sensor_numbers, sensor_starts, sensor_ends, butterworth_arrays, bandpass_arrays = [], [], [], [], [], []
        for result_item in annotation_result:
            events.append(result_item['value']['timeserieslabels'])
            sensor_numbers.append(annotation_item['data']['sensor'])

            start_index, end_index = result_item['value']['start'], result_item['value']['end']
            sensor_starts.append(start_index + sensor_offset)
            sensor_ends.append(end_index + sensor_offset)

            butterworth_arrays.append(list(signal_data['ax3_butterworth'][start_index:end_index]))
            bandpass_arrays.append(list(signal_data['ax3_bandpass'][start_index:end_index]))

        df = pd.DataFrame({
            'events': events,
            'sensor_numbers': sensor_numbers,
            'sensor_starts': sensor_starts,
            'sensor_ends': sensor_ends,
            'ax3_butterworth': butterworth_arrays,
            'ax3_bandpass': bandpass_arrays,
        })
        print('Saving result to', output_dir)
        os.makedirs(output_dir, exist_ok=True)
        df.to_csv(os.path.join(output_dir, export_filename), index=False)

def process_data(input_data, output_dir):
    with open(input_data) as fin:
        annotation_data = json.load(fin)
        for annotation_item in annotation_data:
            process_annotation(annotation_item, output_dir)

if __name__ == "__main__":
    process_data(path, "./result")