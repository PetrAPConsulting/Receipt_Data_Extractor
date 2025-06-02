# Receipt Data Extractor
Extract structured data from receipt images using Groq's Vision API with Llama 4 Maverick LLM. Automatically processes financial receipts and outputs VAT information, prices, and transaction details in JSON format.

## Features

- 🖼️ Process multiple image formats (JPG, PNG, GIF, BMP)
- 🤖 AI-powered data extraction using Groq's Llama 4 Vision model (inference speed 400 tps)
- 📊 Structured JSON output with VAT and pricing information
- 🔄 Batch processing for multiple receipts
- 🔒 Secure API key management via .env file

## Quick Start

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager
- Groq API key ([Get one here](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone <https://github.com/PetrAPConsulting/Receipt_Data_Extractor>
cd Extractor

# Create virtual environment/Activate
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << EOF
groq
python-dotenv
EOF

# Install dependencies
uv pip install -r requirements.txt

# Set up your API key
echo "GROQ_API_KEY=your-api-key-here" > .env

# Add .env to .gitignore (if using git)
echo ".env" >> .gitignore
echo ".venv/" >> .gitignore

# Run the script
python receipt_extractor.py
```

### Quick one-liner setup (after creating project directory):

```bash
uv venv && source .venv/bin/activate && uv pip install groq python-dotenv && echo "GROQ_API_KEY=your-key-here" > .env
```
### Usage

```bash
# Process all receipts in current directory
python receipt_extractor.py

# Process a specific receipt
python receipt_extractor.py uctenka_001.jpg
```

### Input/Output

Input: Receipt images named like uctenka_001.jpg
Output: JSON files with same base name uctenka_001.json

### API Key Management

```bash
# View current key (masked)
python manage_api_key.py view

# Update key
python manage_api_key.py set gsk_YourNewKey

# Remove key
python manage_api_key.py remove
```

### Troubleshooting

- No API key found: Ensure .env file exists with GROQ_API_KEY=your-key
- JSON parsing error: Model may need clearer prompts for complex receipts
- Image not found: Check file exists and extension is supported
