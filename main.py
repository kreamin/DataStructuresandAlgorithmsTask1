validCommands = [
    'stock', 'order', 'expire', 'return',
    'discount', 'discount_end', 'check', 'profit'
]

storeCosts = 0
currentStock = {}
completedOrders = []
discounts = {}


# ============ Stock Management ============

def stock(item, num, price):
    global storeCosts
    num, price = int(num), float(price)
    if item not in currentStock:
        currentStock[item] = []
    currentStock[item].append({"qty": num, "price": price})
    storeCosts += num*price
    print(f'STOCK {num} {item}(s) for {price} each')


def getPrevOrderLIFO(item, qty, price):
    pulled = []
    idx = len(completedOrders) - 1

    while qty > 0 and idx >= len(completedOrders):
        batch = completedOrders[idx]
        if batch["item"] == item and batch["qty"] > 0:
            if price is None or batch["price"] == price:
                take = min(batch["qty"], qty)
                pulled.append({
                    "qty": take,
                    "sell_price": batch["price"],
                    "cost": batch["cost"]
                })
                qty -= take
        idx += 1

    return pulled, qty


def removeStockFIFO(item, qty):
    removed = []
    while qty > 0 and currentStock.get(item):
        batch = currentStock[item][0]
        if batch["qty"] <= 0:
            currentStock[item].pop(0)
            continue  # skip this batch
        take = min(batch["qty"], qty)
        removed.append({"qty": take, "price": batch["price"]})
        batch["qty"] -= take
        qty -= take
        if batch["qty"] == 0:
            currentStock[item].pop(0)
            continue
    return removed



def order(item, num, price):
    global completedOrders
    num, price = int(num), float(price)

    available_qty = sum(batch["qty"] for batch in currentStock.get(item, []))
    if num > available_qty:
        raise ValueError(
            f"Cannot order {num} {item}(s) -- only {available_qty} in stock."
        )

    finalUnitPrice = price
    if item in discounts and discounts[item]:
        finalUnitPrice *= (1 - discounts[item][-1] / 100)

    removed = removeStockFIFO(item, num)
    orderProfit = 0

    for b in reversed(removed):
        margin = (finalUnitPrice - b["price"]) * b["qty"]
        orderProfit += margin

        completedOrders.append(
            {
                "item": item,
                "qty": b["qty"],
                "disc_price": finalUnitPrice,
                "cost": b["price"],
                "price_paid": price
            }
        )

    print(f"ORDER {item} {num}, profit {orderProfit:.2f}")




def expire(item, num):
    """Expire oldest stock (FIFO loss)."""
    global storeCosts
    num = int(num)
    removed = removeStockFIFO(item, num)
    loss = removed[0]["price"] * removed[0]["qty"]
    print(f"EXPIRE {item} {num}, loss {loss:.2f}")


def returnItem(item, qty, sell_price):
    global completedOrders, storeCosts
    remaining = int(qty)
    refundCost = 0.0


    completedOrders.reverse()

    matching_orders = [
        order for order in completedOrders
        if order["item"] == item and float(order['price_paid']) == float(sell_price)
    ]

    total_sold = sum(o["qty"] for o in matching_orders)
    print(total_sold)

    if remaining > total_sold:
        raise ValueError(
            f"Cannot return {remaining} {item}(s) at {float(sell_price):.2f}\n-- only {total_sold} were sold at that price."
        )

    for order in matching_orders:
        if remaining <= 0:
            break
        take_qty = min(order["qty"], remaining)
        refundCost += (take_qty * order["disc_price"]) - (take_qty * order['cost'])
        remaining -= take_qty

    storeCosts += refundCost
    print(f"RETURN {item} {qty} {sell_price}\nprofit impact -{refundCost:.2f}")
    completedOrders.reverse()




def discount(item, disc):
    disc = int(disc)
    if item not in discounts:
        discounts[item] = []
    discounts[item].append(disc)
    print(f'DISCOUNT {item} by {disc}%')


def discountEnd(item):
    if item in discounts and discounts[item]:
        discounts[item].pop()
        if not discounts[item]:
            discounts.pop(item)
    print(f'DISCOUNT ENDED of {discounts[item][-1]}% on {item}')



def check():
    for item, batches in currentStock.items():
        totalQty = sum(b["qty"] for b in batches)
        print(f"{item}: {totalQty}")


def profit():
    total_sales = sum(batch['qty'] * batch['disc_price'] for batch in completedOrders)

    unsoldStock = 0.0
    for item in currentStock:
        unsoldStock += sum(b["qty"] * b["price"] for b in currentStock[item])

    net_profit = total_sales - storeCosts + unsoldStock
    print(f"Total Store Profit: ${net_profit:.2f}")

# ============ Main ============

def main(file):
    with open(file) as f:
        for line in f:
            parts = line.strip().split(' ')
            if not parts:
                continue

            currCommand = parts[0].lower()
            if currCommand not in validCommands:
                print("Invalid command:", line.strip())
                continue

            try:
                if currCommand == 'stock':
                    stock(parts[1], parts[2], parts[3])  # item, qty, price
                elif currCommand == 'order':
                    order(parts[1], parts[2], parts[3])  # item, qty, price
                elif currCommand == 'expire':
                    expire(parts[1], parts[2])  # item, qty
                elif currCommand == 'return':
                    returnItem(parts[1], parts[2], parts[3])  # item, qty, price
                elif currCommand == 'discount':
                    discount(parts[1], parts[2])  # item, %
                elif currCommand == 'discount_end':
                    discountEnd(parts[1])  # item
                elif currCommand == 'check':
                    check()
                elif currCommand == 'profit':
                    profit()
            except IndexError:
                print("Invalid arguments for command:", line.strip())

            print("-------------------")


if __name__ == "__main__":
    main('./test_cases/input_01.txt')
