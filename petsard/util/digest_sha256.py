import hashlib


def digest_sha256(filepath):
    """
    Calculate SHA-256 value of file. Load 128KB at one time.
    ...
    Args:
        filepath (str) Openable file full path.
    ...
    return:
        (str) SHA-256 value of file.
    """
    sha256hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(131072), b""):
            sha256hash.update(byte_block)
    return sha256hash.hexdigest()
