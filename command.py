import base64
import sys
from removebg import get_executable_directory, RemoveBgDTO, parse_command, is_http_url, resolve_path, process


def manual():
    print("Version: 0.2.3")
    print("Usage: removebg SRC_IMAGE_PATH TARGET_IMAGE_PATH")
    print("or:    removebg SRC_IMAGE_URL TARGET_IMAGE_PATH")
    print("Options Supported:")
    print("\t--rect=rectangle\t\t\toptional, selected rectangle: x,y,width,height")


if __name__ == "__main__":
    # print(f"ROOT: {get_executable_directory()}")
    args = parse_command()
    if len(args.arguments) != 2:
        manual()
        sys.exit(1)
    dto = RemoveBgDTO()
    dto.responseFormat = 1
    if is_http_url(args.arguments[0]):
        dto.url = args.arguments[0]
    else:
        dto.path = resolve_path(args.arguments[0])

    target_path = resolve_path(args.arguments[1])
    if 'rect' in args.parameters:
        value = args.parameters['rect']
        if value:
            ary = value.split(',')
            if len(ary) == 4:
                x = float(ary[0].strip())
                y = float(ary[1].strip())
                w = float(ary[2].strip())
                h = float(ary[3].strip())
                if w > 0 and h > 0 and x >= 0 and y >= 0:
                    dto.selectPolygon = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]

    code, msg, result = process(dto)
    if code != 0:
        sys.stderr.write(f"Error: code={code}, msg={msg}")
        sys.exit(2)
    if len(result) > 0:
        with open(target_path, 'wb') as file:
            file.write(result)
        print(f"Output: {target_path}")
