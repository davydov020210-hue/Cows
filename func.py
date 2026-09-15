import sqlite3, random
import time
con = sqlite3.connect("cows.db")
cur = con.cursor()
MILK_PRICE = 100

def reg(user_id):
    cows = get_cows()
    sql = "INSERT INTO Пользователи(id, Деньги, Молоко, Последние_обновления, "
    for cow in cows:
        sql += f"{cow[4]}, "
    sql = sql[0:-2]
    sql +=f" ) VALUES(?, 5000, 0, {time.time()}, " + "0, "*len(cows)
    sql = sql[0:-2]
    sql += ")"
    cur.execute(sql, (user_id,))
    con.commit()

def get_user(user_id):
    cur.execute("SELECT * FROM Пользователи WHERE id = ?", (user_id,))
    return cur.fetchone()

def add_new_cow(cow_name, cow_income, cow_price, cow_code):
    cur.execute("INSERT INTO Коровы(Название, Доход, Цена, Код) VALUES(?, ?, ?, ?)", (cow_name, cow_income, cow_price, cow_code,))
    con.commit()
    
def register_new_cow(cow_name, cow_income, cow_price, cow_code):
    add_new_cow(cow_name, cow_income, cow_price, cow_code)
    cur.execute(f"ALTER TABLE Пользователи ADD {cow_code} INTEGER DEFAULT 0")
    con.commit()

def add_milk(user_id, count):
    cur.execute("SELECT Молоко FROM Пользователи WHERE id = ?", (user_id,))
    milk = cur.fetchone()[0]
    cur.execute("UPDATE Пользователи SET Молоко = ? WHERE id = ?", (milk + count, user_id,))
    con.commit()

def update(user_id):
    cows = get_cows()
    sql = "SELECT "
    for cow in cows:
        sql += f"{cow[4]}, "
    sql = sql[0:-2]
    sql += " FROM Пользователи WHERE id = ?"
    print(sql)
    print(cows)
    cur.execute(sql, (user_id,))
    res = cur.fetchone()

    total = 0
    for i in range(len(cows)):
        total += res[i] * cows[i][2]

    cur.execute("SELECT Последние_обновления FROM Пользователи WHERE id = ?", (user_id,))
    old_time = cur.fetchone()[0]
    new_time = time.time()
    delta_time = new_time - old_time
    days = delta_time / 86400
    add_milk(user_id, total*days)
    cur.execute("UPDATE Пользователи SET Последние_обновления = ? WHERE id = ?", (new_time, user_id,))

def change_milk_price():
    global MILK_PRICE

    old_price = MILK_PRICE
    MILK_PRICE = random.randint(50, 150)

    print(f"Цена молока изменилась: {old_price} - {MILK_PRICE}")

    return MILK_PRICE

#async def main():
#    task = asyncio.create_task(periodic_task())
#    await task

#if __name__ == "__main__":
#    asyncio.run(main())

def stat(user_id):
    cows = get_cows()
    sql = "SELECT Молоко, Деньги, "
    for cow in cows:
        sql += f"{cow[4]}, "
    sql = sql[0:-2]
    sql += " FROM Пользователи WHERE id = ?"
    print(sql)
    cur.execute(sql, (user_id,))
    res = cur.fetchone()
    print(res)

    milk, money = res[0:2]
    total_cows = 0
    for count in res[2:]:
        total_cows += count
    
    return(f"Деньги: {money}. Молоко: {milk}. Всего коров: {total_cows}")

def get_cow(cow_id):
    cur.execute("SELECT * FROM Коровы WHERE id = ?", (cow_id,))
    result = cur.fetchone()

    return result

def get_cows():
    cur.execute("SELECT * FROM Коровы")
    result = cur.fetchall()
    
    return result

def get_milk_price():
    return MILK_PRICE

def get_cow_price(cow_id):
    cur.execute("SELECT Цена FROM Коровы WHERE id = ?", (cow_id,))
    result = cur.fetchone()
    if result is None:
        return None
    return result[0]

def sell_milk_func(user_id, user_milk_sell):
    cur.execute("SELECT Молоко, Деньги FROM Пользователи WHERE id = ?",(user_id,))
    result = cur.fetchone()

    if result is None:
        return "Пользователь не найден"

    user_milk, user_money = result

    user_milk_sell = int(user_milk_sell)

    if user_milk_sell <= 0:
        return "Количество молока должно быть больше нуля"

    ost = user_milk - user_milk_sell

    if ost < 0:
        return "Недостаточно молока"

    earned_money = user_milk_sell * get_milk_price()
    new_money = user_money + earned_money

    cur.execute("UPDATE Пользователи SET Молоко = ?, Деньги = ? WHERE id = ?",(ost, new_money, user_id))
    con.commit()

    return f"Получено: {earned_money} денег"

def buy_cow_func(user_id, cow_id):
    update(user_id)
    cur.execute("SELECT Деньги FROM Пользователи WHERE id = ?", (user_id,))
    user_balance = cur.fetchone()[0]
    cow = get_cow(cow_id)
    ost = user_balance-cow[3]
    print(ost, user_balance, cow[3])
    if ost >= 0:
        cur.execute("UPDATE Пользователи SET Деньги = ? WHERE id = ?", (ost, user_id,))
        cur.execute(f"UPDATE Пользователи SET {cow[4]} = {cow[4]} + 1 WHERE id = ?", (user_id,))
        con.commit()

        return True
    else:
        return False
    

def my_cows_func(user_id):
    cows = get_cows()
    sql = "SELECT "
    for cow in cows:
        sql += f"{cow[4]}, "
    sql = sql[0:-2]
    sql += " FROM Пользователи WHERE id = ?"
    cur.execute(sql, (user_id,))
    user_cows = cur.fetchone()

    text = ""
    for i in range(len(cows)):
        text += f"{cows[i][1]}: {user_cows[i]}\n"
    return text