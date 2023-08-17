import uuid


def make_bulk(num, obj):
    bulk = []
    counter = 1
    while counter <= num:
        bulk.append(obj)
        counter += 1
    return bulk
def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'images/{filename}'.format(filename=filename)