from urllib.parse import parse_qs

X = "A=abc&B=123&C=164&C=555a"

print(parse_qs(X))