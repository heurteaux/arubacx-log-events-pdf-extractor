# arubacx-pdf-extractor

## Description
[`arubacx-log-events-pdf-extractor`](command:_github.copilot.openSymbolFromReferences?%5B%22arubacx-pdf-extractor%22%2C%5B%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2FUsers%2Fcheurteaux%2FDocuments%2Fcode%2Farubacx-pdf-extractor%2Fpyproject.toml%22%2C%22external%22%3A%22file%3A%2F%2F%2FUsers%2Fcheurteaux%2FDocuments%2Fcode%2Farubacx-pdf-extractor%2Fpyproject.toml%22%2C%22path%22%3A%22%2FUsers%2Fcheurteaux%2FDocuments%2Fcode%2Farubacx-pdf-extractor%2Fpyproject.toml%22%2C%22scheme%22%3A%22file%22%7D%2C%22pos%22%3A%7B%22line%22%3A1%2C%22character%22%3A8%7D%7D%5D%5D "Go to definition") is a tool designed to convert ArubaCX PDF log events documentation into a usable JSON file. It leverages OpenAI's API to sanitize and process the log events.

## Requirements
- Python 3.13 or higher
- Poetry for dependency management

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/heurteaux/arubacx-log-events-pdf-extractor/tree/master
    cd arubacx-log-events-pdf-extractor
    ```

2. **Install dependencies using Poetry:**
    ```sh
    poetry install
    ```

3. **Set up environment variables:**
    Create a [`.env`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fcheurteaux%2FDocuments%2Fcode%2Farubacx-pdf-extractor%2F.env%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/cheurteaux/Documents/code/arubacx-pdf-extractor/.env") file in the root directory and add your OpenAI API key:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Usage

1. **Prepare your PDF file:**
    Ensure you have the PDF file containing the ArubaCX log events that you want to convert.

2. **Run the script:**
    ```sh
    poetry run python run.py <path_to_pdf> <path_to_output_json>
    OR
    ./run.py <path_to_pdf> <path_to_output_json>
    ```
    Replace `<path_to_pdf>` with the path to your source PDF file and `<path_to_output_json>` with the desired path for the output JSON file.

### Example
```sh
./run.py ./logs/arubacx_logs.pdf ./output/logs.json
```

## Features
- Converts ArubaCX PDF log events to JSON format.
- Utilizes OpenAI's API for sanitization and processing.
- Supports session resumption in case of interruptions.

## Why use an LLM ?

Because it is the most efficient way to sanitize the content of an unstructured document such as pdf.
It isn't perfect and can make errors or output irrelevant logs so be careful but as the usecase isn't critical
the use of such a technology was the most efficient way to achieve good results. The extraction work is performed 
by a regex rather than the LLM.

## OpenAPI cost ?

For 8k log events it cost me less than 0.25€.

## Contact
For any questions or issues, please contact Colin Heurteaux at dev@heurteaux.me.