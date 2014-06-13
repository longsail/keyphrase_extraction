#coding=utf-8
with open("世界杯",'r') as f:
    lines = f.readlines()
spe_chr = chr(29)
content = list(set(line.split(spe_chr)[2] for line in lines))
string_to_file = '\n'.join(content)
with open('test.txt','w') as f:
    f.write(string_to_file)

