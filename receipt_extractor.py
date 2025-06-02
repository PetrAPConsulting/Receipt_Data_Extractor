from groq import Groq
import base64
import os
import json
import glob
from typing import Dict, Any, Optional

# Optional: Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip .env file loading
    pass

# Function to encode the image
def encode_image(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def create_extraction_prompt(system_prompt: str, json_schema: Dict[str, Any]) -> str:
    """Create the full extraction prompt with system instructions and schema."""
    prompt = f"""{system_prompt}

Please extract the information according to this JSON schema:
{json.dumps(json_schema, indent=2)}

Return ONLY valid JSON that matches this schema. Do not include any explanatory text."""
    return prompt

def extract_receipt_data(image_path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Extract receipt data from an image using Groq API."""
    
    # Initialize Groq client
    client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
    
    # System prompt
    system_prompt = """Extract the following details from the provided image of receipt document. First look for VAT identification number (vatNumber) in the document and associated name of the company (companyName).
Ensure all fields from the schema are populated if the information is present in the document. If a piece of information is not found, you may omit the field or use a suitable placeholder like 'N/A' if the schema requires it, but prioritize extracting actual values. For numerical values (prices, VAT amount, VAT rate), provide them as numbers (float).
For VAT rate, if it's written as e.g. '21%', provide the number 21. Also, extract the date of sale (transaction date) from the receipt always in dd.mm.yyyy format. It might be in dd/mm/yyyy or dd.mm.yyyy format on document. If multiple dates are present (e.g., issue date, due date), use the primary transaction sale date."""

    # JSON schema
    json_schema = {
        "type": "object",
        "required": ["companyName", "vatNumber", "priceWithoutVAT", "vat", "vatRate", "priceIncludingVAT", "dateOfSale"],
        "properties": {
            "companyName": {
                "type": "string",
                "description": "The legal name of the company that issued the receipt always associated with the VAT identification number. Legal name always includes legal form (e.g. s.r.o., a.s. etc.)"
            },
            "vatNumber": {
                "type": "string",
                "description": "The VAT identification number of the company."
            },
            "priceWithoutVAT": {
                "type": "number",
                "format": "float",
                "description": "The total price of goods/services before VAT is applied. Use 0.0 if not explicitly found."
            },
            "vat": {
                "type": "number",
                "format": "float",
                "description": "The total VAT amount charged. Use 0.0 if not explicitly found."
            },
            "vatRate": {
                "type": "number",
                "format": "float",
                "description": "The VAT rate as a percentage (e.g., 21 for 21%). Use 0.0 if not explicitly found."
            },
            "priceIncludingVAT": {
                "type": "number",
                "format": "float",
                "description": "The final price including VAT. This is usually the most prominent total amount."
            },
            "dateOfSale": {
                "type": "string",
                "description": "The date of sale or transaction date from the receipt, in dd.mm.yyyy format."
            }
        }
    }
    
    # Encode the image
    base64_image = encode_image(image_path)
    
    # Create the full prompt
    extraction_prompt = create_extraction_prompt(system_prompt, json_schema)
    
    try:
        # Make API call
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": extraction_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.2,  # Lower temperature for more consistent extraction
            max_tokens=1000
        )
        
        # Get the response
        response_content = chat_completion.choices[0].message.content
        
        # Parse JSON from response
        # Try to extract JSON from the response in case there's extra text
        try:
            # First try direct parsing
            extracted_data = json.loads(response_content)
        except json.JSONDecodeError:
            # If that fails, try to find JSON in the response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_content)
            if json_match:
                extracted_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not find valid JSON in the response")
        
        return extracted_data
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def get_json_filename(image_path: str) -> str:
    """Generate JSON filename maintaining the original naming logic."""
    # Get the base filename without extension
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    # Create JSON filename with the same base name
    return f"{base_name}.json"

def process_all_receipts(directory: str = ".") -> None:
    """Process all image files in the specified directory."""
    
    # Get all image files in the directory
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
        image_files.extend(glob.glob(os.path.join(directory, ext.upper())))
    
    if not image_files:
        print(f"No image files found in {directory}")
        return
    
    print(f"Found {len(image_files)} image(s) to process")
    
    # Process each image
    successful_count = 0
    for image_path in image_files:
        print(f"\nProcessing: {os.path.basename(image_path)}")
        
        extracted_data = extract_receipt_data(image_path)
        
        if extracted_data:
            # Generate JSON filename maintaining original naming
            json_filename = get_json_filename(image_path)
            
            # Save individual result to JSON file
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Successfully extracted data from {os.path.basename(image_path)}")
            print(f"   Saved to: {json_filename}")
            print(json.dumps(extracted_data, indent=2))
            successful_count += 1
        else:
            print(f"❌ Failed to extract data from {os.path.basename(image_path)}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Processing complete: {successful_count}/{len(image_files)} files processed successfully")

def main():
    """Main function to run the receipt extraction."""
    
    # Check if API key is set
    if not os.environ.get("GROQ_API_KEY"):
        print("Please set the GROQ_API_KEY environment variable")
        print("You can do this by:")
        print("  - Adding it to your .env file: GROQ_API_KEY=your-api-key-here")
        print("  - Or setting it in your shell: export GROQ_API_KEY='your-api-key-here'")
        return
    
    # Process single file or all files
    import sys
    
    if len(sys.argv) > 1:
        # Process specific file
        image_path = sys.argv[1]
        if os.path.exists(image_path):
            print(f"Processing single file: {image_path}")
            result = extract_receipt_data(image_path)
            if result:
                print("\nExtracted data:")
                print(json.dumps(result, indent=2))
                
                # Save to JSON file with same base name
                json_filename = get_json_filename(image_path)
                with open(json_filename, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Result saved to {json_filename}")
            else:
                print("Failed to extract data")
        else:
            print(f"File not found: {image_path}")
    else:
        # Process all images in current directory
        process_all_receipts()

if __name__ == "__main__":
    main()
