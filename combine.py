import os


def combine_mdx_files(directory, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, _, files in os.walk(directory):
            for filename in files:
                if filename.endswith(".mdx"):
                    with open(
                        os.path.join(root, filename), "r", encoding="utf-8"
                    ) as infile:
                        outfile.write(infile.read())
                        outfile.write("\n\n")


if __name__ == "__main__":
    combine_mdx_files("./nodes", "combined_docs.mdx")
