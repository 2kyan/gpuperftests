# Assuming the necessary imports
import argparse
import glob
import os
import sys

filename_allowed_chars = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class FileList:
    def __init__(self):
        self.file_list = []
        self.capacity = 16

    def add_file(self, file: str) -> bool:
        if len(self.file_list) == self.capacity:
            self.capacity *= 2
            # Python's list manages its own memory, so no need for explicit reallocation
        self.file_list.append(file)
        return True

def sanitize_file(content: bytes) -> str:
    result_data = []

    for byte in content:
        if byte > 99:
            result_data.append(f"{byte // 100}")
            result_data.append(f"{(byte % 100) // 10}")
            result_data.append(f"{byte % 10}")
        elif byte > 9:
            result_data.append(f"{byte // 10}")
            result_data.append(f"{byte % 10}")
        else:
            result_data.append(f"{byte}")
        result_data.append(",")

    # Remove the last comma
    if result_data:
        result_data.pop()

    return ''.join(result_data)

def read_file(filepath, verbose=False):
    try:
        with open(filepath, 'rb') as file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0, os.SEEK_SET)

            if verbose:
                print(f"File size: {file_size}")

            buffer = file.read(file_size)
            return buffer, file_size

    except Exception as e:
        print(f"Failed to read file: {filepath}, Error: {e}")
        return None, 0

def process_wildcard_filename(wildcard_name: str, file_list: FileList) -> bool:
    wildcard_ptr = wildcard_name.find('*')
    if wildcard_ptr == -1:
        return False

    try:
        for file in glob.glob(wildcard_name):
            if os.path.isfile(file):
                if not file_list.add_file(file):
                    return False
    except Exception as e:
        print(f"Failed to list wildcard: {wildcard_name}, Error: {e}")
        return False

    return True

# filename_allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-_"
# filename_allowed_chars = "_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def sanitize_output_filename(output_filename: str) -> str:
    # Extract the filename from the path
    sanitized_output_filename = os.path.basename(output_filename)

    # Replace disallowed characters
    sanitized_output_filename = ''.join(
        c if c in filename_allowed_chars else '_' for c in sanitized_output_filename
    )

    return sanitized_output_filename

def main(argv):
    file_list = FileList()
    size_print_buffer = "32"
    output_filename = None
    capturing_output_name = False
    verbose = False

    for arg in argv[1:]:
        if arg in ("-o", "-O"):
            capturing_output_name = True
        elif arg in ("-v", "-V"):
            verbose = True
        else:
            if capturing_output_name:
                output_filename = arg
                capturing_output_name = False
            else:
                if '*' in arg:
                    if not process_wildcard_filename(arg, file_list):
                        print("An error occurred while processing arguments, aborting!")
                        return 1
                else:
                    if not file_list.add_file(arg):
                        print("An error occurred while processing arguments, aborting!")
                        return 1

    if output_filename is None:
        print("No output filename given, aborting!")
        return 1

    if verbose:
        print(f"Output header file: {output_filename}")

    try:
        with open(output_filename, "wb") as output_file:
            sanitized_output_filename = sanitize_output_filename(output_filename)
            if sanitized_output_filename is None:
                print("Failed to write #ifdef")
                return 1

            output_file.write(b"// !!! THIS FILE IS MACHINE GENERATED, ANY EDITS WILL BE OVERWRITTEN !!!\n\n")
            output_file.write(b"#ifndef _AB_EMBEDDED_RESOURCES_" + sanitized_output_filename.encode() + b"\n#define _AB_EMBEDDED_RESOURCES_" + sanitized_output_filename.encode() + b"\n\n#ifdef EMBED_RESOURCES\n\n")

            output_file.write(b"#ifndef _AB_EMBEDDED_RESOURCE_STRUCT_DEFINED\n")
            output_file.write(b"#define _AB_EMBEDDED_RESOURCE_STRUCT_DEFINED\n")
            output_file.write(b"struct _ab_embedded_resource_t {\n")
            output_file.write(b"    const char *file_name;\n")
            output_file.write(b"    size_t file_size;\n")
            output_file.write(b"    const unsigned char *file_data;\n")
            output_file.write(b"};\n")
            output_file.write(b"#endif\n\n")

            output_file.write(b"static size_t ab_embedded_resource_count_" + sanitized_output_filename.encode() + b" = " + str(len(file_list.file_list)).encode() + b";\n")

            file_content_sizes = []

            err = False
            for i, filename in enumerate(file_list.file_list):
                filename_top = os.path.basename(filename)
                if verbose:
                    print(f"Processing {filename_top} ({filename})")
                file_content, file_size = read_file(filename, verbose)
                if file_content is None:
                    err = True
                    break
                sanitized_content = sanitize_file(file_content)
                if sanitized_content is None:
                    err = True
                    break
                file_content_sizes.append(file_size)
                if verbose:
                    print(f"Sanitized size: {len(sanitized_content)}")

                output_file.write(b"static const unsigned char ab_embedded_resources_" + sanitized_output_filename.encode() + b"_content_" + str(i).encode() + b"[] = {\n    ")
                output_file.write(sanitized_content.encode())
                output_file.write(b"\n};\n")

            output_file.write(b"\nstatic struct _ab_embedded_resource_t ab_embedded_resources_" + sanitized_output_filename.encode() + b"[] = {\n")

            for i, filename in enumerate(file_list.file_list):
                filename_top = os.path.basename(filename)
                file_size = file_content_sizes[i]

                output_file.write(b"{\n    \"" + filename_top.encode() + b"\",\n    " + str(file_size).encode() + b",\n    ab_embedded_resources_" + sanitized_output_filename.encode() + b"_content_" + str(i).encode())
                if i + 1 < len(file_list.file_list):
                    output_file.write(b"\n},\n")
                else:
                    output_file.write(b"\n}\n")

            output_file.write(b"};\n\n")
            output_file.write(b"#endif\n#endif")

        if err:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"Failed to open output file: {output_filename}, Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))

