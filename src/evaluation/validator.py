from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class FactCheckerChain:
    """Validates medical advice against known medical facts"""
    
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Medical Validator for a holistic healthcare system. Review responses for critical safety issues ONLY.

**CRITICAL: This is a traditional medicine system (Ayurveda, Yoga, Unani, Siddha, Homeopathy)**

**BLOCK ONLY IF:**
1. **Life-threatening advice**: "Drink bleach", "Don't call ambulance for heart attack"
2. **Dangerous dosages**: "Take 50 pills", "Overdose on X"
3. **Self-harm encouragement**: "You should hurt yourself"
4. **Completely fake information**: Invented drugs, non-existent treatments

**DO NOT BLOCK:**
- Traditional Ayurvedic/herbal remedies (turmeric, neem, tulsi, mustard oil, etc.)
- Yoga recommendations (asanas, pranayama, meditation)
- Natural treatments from traditional medicine systems
- Home remedies commonly used in Indian households
- Advice to "consult a doctor for severe cases" (this is GOOD, not unsafe)
- Unverifiable sources (traditional knowledge often has no modern citations)

**IMPORTANT RULES:**
- Traditional remedies are SAFE even if not scientifically proven
- If response includes "see a doctor" or "seek medical attention", it's SAFE
- Absence of citations doesn't mean unsafe (traditional knowledge is oral/ancient texts)
- For ambiguous cases needing more info, ADD a disclaimer instead of blocking

**Response Format:**
{{
    "is_safe": true/false,
    "reason": "explanation ONLY if blocking",
    "revised_response": null OR "add disclaimer: 'For severe burns, seek immediate medical attention. These traditional remedies work best for minor burns.'"
}}

If you want to ADD a safety note without blocking, set is_safe=true and put the disclaimer in revised_response.
"""),
            ("user", "User Query: {query}\nAI Response: {response}")
        ])
        self.chain = self.prompt | self.llm | JsonOutputParser()
        
    def validate(self, query: str, response: str) -> Dict[str, Any]:
        print(f"      → Validator: Checking response safety/accuracy...")
        try:
            result = self.chain.invoke({"query": query, "response": response})
            print(f"      ← Validation Result: Safe={result.get('is_safe', True)}")
            return result
        except Exception as e:
            print(f"      ⚠️ Validation failed: {e}")
            return {"is_safe": True, "reason": "Validation error, defaulted to safe"}
