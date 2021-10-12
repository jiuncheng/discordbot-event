import datetime

now = datetime.datetime.utcnow().replace(second=0, microsecond=0)
time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(microsecond=0, second=0)

data = (time - now).total_seconds()
print(data)