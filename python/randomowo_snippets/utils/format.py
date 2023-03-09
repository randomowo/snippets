def duration_from_ts(total_seconds: int | float) -> str:
    a, b = total_seconds, 0
    result = []
    for symbol, div in (('s', 1), ('m', 60), ('h', 60), ('d', 24), ('w', 7), ('y', 52)):
        a, b = divmod(a, div)
        if a == 0:
            break

        if result:
            result[-1] = (result[-1][0], b)

        result.append((symbol, a))

    return ' '.join(
        map(
            lambda pair: f'{int(pair[1])}{pair[0]}',
            filter(lambda p: p[1], reversed(result))
        )
    )
