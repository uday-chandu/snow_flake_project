def is_prime(prime_number):
  number=prime_number
  count=0
  for i in range(2,number):
    if number%i==0:
    #   print(i)
      count=count+1
  if number <2:
    count=1
  return (f"{number} is not a prime number " if count>0 else f"{number} is prime number")

for j in range(1,10):
  print(is_prime(j))


import datetime
d='21-09-2026'
print(datetime.datetime.strptime(d,'%d-%m-%Y')+datetime.timedelta(days=2))


def wrapper(func):
  def welcome():
    print('hello world')
    func()
    print('second print statement')
  return welcome
@wrapper
def print_function():
  print('hello uday')

print_function()