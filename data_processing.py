import csv,sys
with open("ratio.csv") as f:
    f_csv = csv.DictReader(f)
    cur_n = 0
    cur_u = 0
    cur_entropy = 0
    for row in f_csv:
        if cur_u != row['u'] or cur_n != row['n']:
            if cur_u != 0:
                with open("ratio_result.csv", "a", newline='') as output:
                    output_csv = csv.writer(output)
                    output_csv.writerow((cur_u, cur_n, cur_entropy))
                print(cur_entropy)
            cur_u = row['u']
            cur_n = row['n']
            cur_entropy = float(row['ratio']) / 20
        else:
            cur_entropy += float(row['ratio']) / 20

    print (cur_entropy)
