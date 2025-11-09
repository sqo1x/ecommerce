def solve():
    n = int(input())
    a, b, c = map(int, input().split())

    # Создаем массив для отслеживания достижимых сумм
    dp = [False] * (n + 1)

    # Изначально у нас есть 1 рубль
    dp[1] = True

    # Перебираем все суммы от 1 до n
    for i in range(1, n + 1):
        if dp[i]:
            # Если текущую сумму можно набрать, то можно добавить монеты
            if i + a <= n:
                dp[i + a] = True
            if i + b <= n:
                dp[i + b] = True
            if i + c <= n:
                dp[i + c] = True

    # Считаем количество достижимых сумм
    result = sum(1 for i in range(1, n + 1) if dp[i])
    return result


print(solve())