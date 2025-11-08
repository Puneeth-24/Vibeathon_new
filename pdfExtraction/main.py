import argparse
import json
import sys

from pdfminer.high_level import extract_text


def is_heading(line):
    line_clean = line.strip()
    if not line_clean:
        return False

    # Mostly uppercase → heading
    if line_clean.isupper():
        return True

    # Short Title Case → heading
    words = line_clean.split()
    if len(words) <= 8 and all(w[0].isupper() for w in words if w.isalpha()):
        return True

    return False


def extract_topics_and_content(pdf_path):
    text = extract_text(pdf_path)
    lines = text.split("\n")

    results = []
    current_topic = None
    current_content = []

    for line in lines:
        if is_heading(line):
            if current_topic:
                results.append(
                    {
                        "topic": current_topic.strip(),
                        "content": "\n".join(current_content).strip(),
                    }
                )
                current_content = []

            current_topic = line.strip()

        else:
            current_content.append(line)

    # Add the last topic at the end
    if current_topic:
        results.append(
            {
                "topic": current_topic.strip(),
                "content": "\n".join(current_content).strip(),
            }
        )

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract topics and content from a PDF file."
    )
    parser.add_argument("pdf_file", help="The path to the PDF file to process.")
    args = parser.parse_args()

    extracted_data = extract_topics_and_content(args.pdf_file)
    json.dump(extracted_data, sys.stdout, ensure_ascii=False, indent=4)
