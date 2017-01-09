
def parse_version_str( version_str ):
    parts = version_str.strip().split('.')
    major = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])

    return (major, minor, patch)
