# def foo(deck, *, h=5):
#     print(deck, h)
# import random
# deck = [1, 2, 3, 4, 5, 6, 7, 8, 9]
# d = random.shuffle(deck)
# print(d)
#
# from functools import partial
#
# def print_sum(num_list, msg=None):
#     total = sum(num_list)
#     print(f"{msg}: {total}" if msg else total)
#
#
# c_t_c = partial(print_sum, [1,2,3,4])
# c_t_c([5,6])

# def double():
#     x = 5
#     def inner_doubler(loc_x):
#         # global x
#         return loc_x * 2
#     return inner_doubler(x)
# x = 2
#
# y = double()
# # print(y)
#
# def foo(a,b,c,*,d,e=1):
#     pass
from itertools import groupby

# dictionary
INFO = [
    {"language": "java", "name": "Spring"},
    {"language": "javascript", "name": "React"},
    {"language": "javascript", "name": "Svelte"},
    {"language": "python", "name": "Django"},
    {"language": "python", "name": "Flask"},
    {"language": "ruby", "name": "Ruby on Rails"},
]


# define a function for key
def key_func(k):
    return k["language"]


# sort INFO data by 'company' key.
INFO = sorted(INFO, key=key_func)
new = []
for key, value in groupby(INFO, key_func):
    # print(key)
    # print(list(map(lambda x: x['name'], value)))
    new.append({key: list(map(lambda x: x["name"], value))})

print(new)
