validCommands = ['stock', 'order', 'expire', 'return', 'discount', 'discount_end', 'check', 'profit']

storeMoney = 0.00

currentStock = {}

prevOrders = []

discounts = {}


def stock(item, num, price=None):
    print('stock', item, num, price)
    global storeMoney
    if price:
        storeMoney -= (float(price) * float(num))
        print(storeMoney)
    if item in currentStock:
        currentStock[item] = int(num) + currentStock[item]
    else:
        currentStock[item] = int(num)


def order(item, num, price):
    print('order', item, num, price)
    global storeMoney
    stock(item, -int(num))
    total = float(price) * float(num)
    if item in discounts:
        print('discount applied!', total, total * (1 - (discounts[item] / 100)))
        total *= (1 - (discounts[item] / 100))
    storeMoney += total
    print(storeMoney)


def expire(item, num):
    print('expire', item, num)
    stock(item, -int(num))

    '''needs to calculate loss of FIFO ordered apples
    since 100 apples were ordered at $1.00 each, when 5 expire thats a loss of $5.00
    also, assuming that this example is 1/10 of what these programs will go though
    need to do every case example, eg expiring more items than can handle
    '''

def returnItem(num, price):
    print('return', num, price)
    global storeMoney
    storeMoney -= float(num) * float(price)

def discount(item, disc):
    print('discount', item, disc)
    if item not in discounts:
        discounts[item] = int(disc)

def discountEnd(item):
    print('discount end', item)
    discounts.pop(item)

def check():
    for i in currentStock:
        print(i + ':', currentStock[i])

def profit():
    print('Profit/Loss: $' + str(storeMoney))

def main():
    for line in open('./testFile.txt'):
        currCommand = line.split(' ')[0].strip().lower()
        if currCommand in validCommands:
            commands = line.split(' ')
            if currCommand == 'stock':
                stock(commands[1].strip(), commands[2].strip(), commands[3].strip())
            elif currCommand == 'order':
                order(commands[1].strip(), commands[2].strip(), commands[3].strip())
            elif currCommand == 'expire':
                expire(commands[1].strip(), commands[2].strip())
            elif currCommand == 'return':
                returnItem(commands[2].strip(), commands[3].strip())
            elif currCommand == 'discount':
                discount(commands[1].strip(), commands[2].strip())
            elif currCommand == 'discount_end':
                discountEnd(commands[1].strip())
            elif currCommand == 'check':
                check()
            elif currCommand == 'profit':
                profit()
        else:
            print('invalid command')
        print('-------------------')

main()
