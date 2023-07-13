import re


def url_validator(url: str, *schemas: str) -> tuple[str | None, str | None]:
    joined_schemas = '|'.join([*schemas])

    url = f'{url}.'
    res = re.match(rf'^(?:(?:{joined_schemas})://)?([\w]+\.)+$', url)

    if res:
        return url[:-1], res.group(0)[:-1]
    return None, None
