import random
my_list = list()
for i in range(10):
    my_list.append(random.randint(0, 2))

print(random.choice(my_list))