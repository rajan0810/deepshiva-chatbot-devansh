"""
PDF Medical Document Extractor
Extracts text and structured data from medical reports and prescriptions
"""

from typing import Dict, Any, List
from pathlib import Path
import logging
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


class MedicalDocumentExtractor:
    """Extract and analyze medical documents"""
    
    def __init__(self, llm=None):
        self.llm = llm
        
    def extract_pdf_content(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text content from PDF
        
        Returns:
            Dict with extracted content and metadata
        """
        try:
            loader = PyPDFLoader(str(file_path))
            pages = loader.load()
            
            # Combine all pages
            full_text = "\n\n".join([page.page_content for page in pages])
            
            return {
                "success": True,
                "file_name": file_path.name,
                "num_pages": len(pages),
                "full_text": full_text,
                "pages": [
                    {
                        "page_num": i + 1,
                        "content": page.page_content,
                        "metadata": page.metadata
                    }
                    for i, page in enumerate(pages)
                ],
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_name": file_path.name
            }
    
    def analyze_medical_document(self, text: str) -> Dict[str, Any]:
        """
        Use LLM to extract structured medical information with timeout
        
        Args:
            text: Raw document text
            
        Returns:
            Structured medical data
        """
        if not self.llm:
            return {"analyzed": False, "reason": "No LLM configured"}
        
        try:
            from concurrent.futures import ThreadPoolExecutor, TimeoutError
            import time
            
            def run_analysis():
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a medical document analyzer. Extract key information quickly and concisely.

Extract ONLY the most important details:
- Document type (Lab Report, Prescription, etc.)
- Patient name (if mentioned)
- Key test results or findings
- Medications mentioned
- Diagnoses

Return JSON:
{{
    "document_type": "...",
    "patient_name": "full name or null",
    "findings": ["key finding 1", "key finding 2"],
    "medications": ["med1", "med2"],
    "diagnoses": ["condition1"],
    "test_results": [{{"test": "Hemoglobin", "value": "10.2", "unit": "g/dL", "status": "Low"}}],
    "summary": "One-line summary"
}}"""),
                    ("user", "Analyze this medical document briefly:\n\n{text}")
                ])
                
                parser = JsonOutputParser()
                chain = prompt | self.llm | parser
                return chain.invoke({"text": text[:2000]})  # Reduced from 3000
            
            # Run with 10 second timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_analysis)
                try:
                    result = future.result(timeout=10.0)  # 10 second timeout
                    return {
                        "analyzed": True,
                        **result
                    }
                except TimeoutError:
                    logger.warning("LLM analysis timed out after 10 seconds")
                    return {
                        "analyzed": False,
                        "error": "Analysis timed out",
                        "summary": f"Document uploaded ({len(text)} characters). Analysis pending."
                    }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "analyzed": False,
                "error": str(e),
                "summary": "Document uploaded successfully. Detailed analysis unavailable."
            }
    
    def process_medical_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Complete pipeline: Extract + Analyze
        
        Returns:
            Complete analysis result
        """
        # Extract raw content
        extraction = self.extract_pdf_content(file_path)
        
        if not extraction["success"]:
            return extraction
        
        # Analyze with LLM
        analysis = self.analyze_medical_document(extraction["full_text"])
        
        return {
            **extraction,
            "analysis": analysis,
            "processed_at": datetime.now().isoformat()
        }
