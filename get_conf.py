import codecs
import os

remotes_folder = "../lirc-remotes-code/remotes/"


def get_name(manufacturer: str, conf_file: str) -> str:
    file_path = remotes_folder + manufacturer + "/" + conf_file

    with codecs.open(file_path, mode="r", encoding="utf8", errors="ignore") as file:
        for each_line in file:
            stripped = each_line.strip()
            if stripped.startswith("begin remote"):
                break

        for each_line in file:
            stripped = each_line.strip()
            if stripped.startswith("name"):
                name = stripped[4:].strip()
                return name.replace("_", " ")

    return conf_file


def main():

    directories = tuple(
        _x
        for _x in os.listdir(remotes_folder)
        if os.path.isdir(remotes_folder + _x)
    )

    conf_files = {
        _d: tuple(
            _c
            for _c in os.listdir(remotes_folder + _d)
            if os.path.isfile(remotes_folder + _d + "/" + _c) and _c.endswith(".conf")
        )
        for _d in directories
    }

    for k, values in conf_files.items():
        for v in values:
            print("{:s}, {:s}: {:s}".format(k, v, get_name(k, v)))


if __name__ == "__main__":
    main()
