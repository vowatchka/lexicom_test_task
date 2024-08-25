import random
import string

NAZVANIE = "nazvanie"


def make_file_extension() -> str:
    extensions = ("wav", "mp3", None)
    extension = random.choice(extensions)
    if not extension:
        extension = ""
        for _ in range(3):
            extension += random.choice(string.ascii_letters)
    return extension


def make_dump_head(table_name: str) -> str:
    return f"""drop table if exists {table_name};

create table {table_name} (
    name text not null,
    status bit(1) {'not null' if table_name == "short_names" else ''}
);

copy {table_name} (name, status) from stdin;\n"""


def make_dump_tail() -> str:
    return "\.\n"


def make_short_names_dump() -> str:
    dump = ""
    for i in range(1, 700_001):
        dump += f"{NAZVANIE}{i}\t{random.randint(0, 1)}\n"
    return dump


def make_full_names_dump() -> str:
    dump = ""
    for i in range(1, 500_001):
        dump += f"{NAZVANIE}{random.randint(1, 700_000)}\t\\N\n"
    return dump


if __name__ == "__main__":
    short_names_dump = make_dump_head("short_names")
    short_names_dump += make_short_names_dump()
    short_names_dump += make_dump_tail()

    with open("sql/short_names_dump.sql", "w", encoding="utf-8") as f:
        f.write(short_names_dump)

    full_names_dump = make_dump_head("full_names")
    full_names_dump += make_full_names_dump()
    full_names_dump += make_dump_tail()

    with open("sql/full_names_dump.sql", "w", encoding="utf-8") as f:
        f.write(full_names_dump)
