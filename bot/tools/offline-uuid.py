import hashlib

def get_offline_uuid(username):
    offline_prefix = f"OfflinePlayer:{username}"
    md5_hash = hashlib.md5(offline_prefix.encode('utf-8')).digest()

    uuid = bytearray(md5_hash)
    uuid[6] &= 0x0F
    uuid[6] |= 0x30
    uuid[8] &= 0x3F
    uuid[8] |= 0x80

    uuid_with_hyphen = f"{uuid[0:4].hex()}-{uuid[4:6].hex()}-{uuid[6:8].hex()}-{uuid[8:10].hex()}-{uuid[10:].hex()}"
    return uuid_with_hyphen

final = get_offline_uuid("test")

if final == "530fa97a-357f-3c19-94d3-0c5c65c18fe8":
    print(True)
    print(final)
else:
    print(False)
    print(final)



