import json 
import os

root_path = os.path.join('/work', 'conspiracies', 'data', 'triplet-extraction-gpt', 'predictions')


template_numbers = [3, 4]

for n in template_numbers:
    out_file = f'prompt_outputs_template_{n}.txt'
    with open(out_file, 'w') as f:
        f.write("")
    prediction_files = [name for name in os.listdir(root_path) if name.startswith(f'template{n}_gpt')]
    example_files = [name for name in os.listdir(root_path) if name.startswith(f'template{n}_examples')]

    for file in prediction_files:
        new_file = f'\n\n#### Output from file {file}\n'
        with open(out_file, 'a') as f:
            f.write(new_file)
        print(new_file)
        with open(os.path.join(root_path, file)) as f:
            data = json.load(f)
        
        if n == 3:
            for d in data: 
                input_text = f'\nInput tweet: {d["tweet"]}\nOutput:\n'
                header = f"| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |\n|{d['tweet']}|"
                with open(out_file, 'a') as f:
                    f.write(input_text)
                    f.write(header)
                    f.write(d['triplets'])
                    f.write("\n")
                print(input_text)
                print(header)
                print(d['triplets'])
                print("\n")

        elif n == 4:
            for d in data:
                tweet = f'\n\nInput tweet: {d["tweet"]}\nTriplets extracted:\n'
                header = "| Subject | Predicate | Object |\n| --- | --- | --- |\n"
                triplets = d["triplets"]
                with open(out_file, 'a') as f:
                    f.write(tweet)
                    f.write(header)
                    f.write(triplets)
                print(tweet)
                print(header)
                print(triplets)
