import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-V3-0324")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or "EMPTY"

client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

SYSTEM_PROMPT = """You are an expert HR recruiter and resume screener.
You must return a JSON object with exactly these fields:
{
  "decision": "SHORTLIST, REJECT, or REVIEW",
  "skills_match_score": <float 0.0-1.0>,
  "experience_match_score": <float 0.0-1.0>,
  "education_match_score": <float 0.0-1.0>,
  "justification": "<detailed justification>"
}"""

def evaluate_sample(resume, jd):
    prompt = f"## Job Requirements:\n{jd}\n\n## Candidate Resume:\n{resume}\n\nAnalyze the fit and return JSON."
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return str(e)

def main():
    print("Fetching from Hugging Face dataset 'cnamuangtoun/resume-job-description-fit' via Datasets API...")
    url = "https://datasets-server.huggingface.co/rows?dataset=cnamuangtoun%2Fresume-job-description-fit&config=default&split=train&offset=0&length=3"
    
    response = requests.get(url)
    data = response.json()
    rows = data.get("rows", [])
    
    output_data = []
    
    for i, item in enumerate(rows):
        row = item.get("row", {})
        resume_text = str(row.get("resume_text", ""))[:1500]
        jd_text = str(row.get("job_description_text", ""))[:1500]
        label = row.get("label", "Unknown")
        
        result_str = evaluate_sample(resume_text, jd_text)
        
        try:
            # Clean up potential markdown formatting
            clean_str = result_str.replace("```json", "").replace("```", "").strip()
            result_json = json.loads(clean_str)
        except Exception:
            result_json = {"error": "Failed to parse JSON", "raw": result_str}
            
        output_data.append({
            "sample_index": i + 1,
            "actual_label": label,
            "jd_snippet": jd_text[:150],
            "llm_evaluation": result_json
        })

    with open("evaluate_results.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print("Results saved to evaluate_results.json")

if __name__ == "__main__":
    main()
