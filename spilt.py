import json

f = open('test.tab')

head = f.readline()

json = "{}"

norm = ""

err = head

for line in f:
    tmp = line.split('\t');
    if '{' in tmp[5]:
        err = err + line
    else:
        norm = norm + "{"
        for tl in tmp:
            norm[]
            for hl in head:
                norm =
        norm = norm + "}"
        norm = norm + line

# e = open('errs','w')
# e.write(err)
# e.close()

# n = open('norms','w')
# n.write(norm)
# n.close()

f.close()
