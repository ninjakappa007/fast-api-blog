

def flat(val):
    result = []
    for i in val:
        if isinstance(i, list):
            result.extend(flat(i))
        else:
            result.append(i)
    return result

l = [1,2,3,[4,5,[6,7]]]

op = flat(l)
print(op)