"""
File processing service for medical reports and images
Supports PDF, images with OCR, and AI-powered analysis
"""
from typing import Dict, Any
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.core.config import settings

try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False


class FileProcessorService:
    """
    Process medical documents:
    - Extract text from PDFs
    - OCR on images
    - AI analysis of medical content
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",  # Supports vision
            temperature=0.3,
            api_key=settings.OPENAI_API_KEY
        )
        # Import here to avoid circular dependency
        from app.services.external_apis import MedicalAPIService
        self.api_service = MedicalAPIService()

    async def process_medical_document(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Extract text/data from medical documents

        Args:
            file_path: Path to the file
            file_type: File extension (.pdf, .jpg, etc.)

        Returns:
            Dict with extracted text and metadata
        """
        file_type = file_type.lower()

        if file_type == '.pdf':
            return await self._process_pdf(file_path)
        elif file_type in ['.jpg', '.jpeg', '.png', '.tif', '.tiff']:
            return await self._process_image(file_path)
        else:
            return {"error": "Unsupported file type"}

    async def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        if not HAS_PDF:
            return {"error": "PDF processing not available"}

        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return {
                "text": text,
                "pages": len(reader.pages),
                "source": "pdf"
            }
        except Exception as e:
            return {"error": str(e)}

    async def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Extract text from image using FREE OCR.space API"""
        try:
            # Use free OCR.space API (no API key required)
            ocr_result = await self.api_service.extract_text_from_image(file_path=file_path)

            if ocr_result.get("success"):
                text = ocr_result.get("extracted_text", "")
                return {
                    "text": text if text else "No text could be extracted from the image",
                    "source": "image_ocr_free",
                    "ocr_confidence": ocr_result.get("confidence", 0),
                    "processing_time_ms": ocr_result.get("processing_time", 0)
                }
            else:
                # OCR failed, try to get image metadata
                error_msg = ocr_result.get("error", "OCR extraction failed")

                # Try to at least get image dimensions
                try:
                    if HAS_OCR:  # PIL is available
                        image = Image.open(file_path)
                        return {
                            "text": f"Image uploaded. {error_msg}",
                            "width": image.width,
                            "height": image.height,
                            "source": "image"
                        }
                except:
                    pass

                return {
                    "text": f"Image uploaded. {error_msg}",
                    "source": "image"
                }

        except Exception as e:
            return {"error": str(e)}

    async def analyze_report(
        self,
        parsed_data: Dict[str, Any],
        report_type: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use AI to analyze medical report content

        Args:
            parsed_data: Extracted text/data from document
            report_type: Type of report (blood_test, imaging, etc.)
            user_context: User's medical conditions and medications

        Returns:
            Dict with AI analysis
        """
        if "error" in parsed_data:
            return {"summary": "Could not analyze report due to processing error"}

        text = parsed_data.get("text", "")

        if not text or len(text.strip()) < 10:
            return {"summary": "No readable text found in document"}

        # Create analysis prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical document analyzer. Analyze the medical report and provide:

1. **Summary**: Brief overview of the report
2. **Key Findings**: Important results, abnormal values
3. **Concerns**: Any values outside normal ranges
4. **Recommendations**: Suggested follow-up actions
5. **Plain Language**: Explain medical terms in simple language

User's Context:
- Existing Conditions: {conditions}
- Current Medications: {medications}

Report Type: {report_type}

Be empathetic and clear. Flag urgent concerns clearly.
"""),
            ("user", "Here is the medical report text:\n\n{report_text}")
        ])

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    report_text=text[:8000],  # Limit text length
                    report_type=report_type,
                    conditions=user_context.get("conditions", []),
                    medications=user_context.get("medications", [])
                )
            )

            return {
                "summary": response.content,
                "analyzed": True
            }

        except Exception as e:
            return {
                "summary": f"Analysis error: {str(e)}",
                "analyzed": False
            }

    async def analyze_symptom_image(self, image_path: str, description: str = "") -> Dict[str, Any]:
        """
        Use GPT-4 Vision to analyze symptom images (rash, wound, etc.)

        Args:
            image_path: Path to image
            description: User's description of symptom

        Returns:
            Dict with AI observations
        """
        # Note: This requires GPT-4 Vision API
        # For now, return placeholder
        return {
            "observation": "Image uploaded successfully. AI vision analysis requires GPT-4V API integration.",
            "user_description": description,
            "recommendation": "Consult with a healthcare provider for proper diagnosis."
        }

    async def extract_structured_data(self, report_text: str, report_type: str) -> Dict[str, Any]:
        """
        Extract structured medical data from report text

        Args:
            report_text: Raw text from medical report
            report_type: Type of medical report

        Returns:
            Dict with structured extracted data
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical data extraction specialist. Extract structured data from medical reports.

For BLOOD_TEST reports, extract:
- Test name, value, unit, reference range, status (normal/abnormal)

For IMAGING reports, extract:
- Body part examined, findings, impressions, recommendations

For PRESCRIPTION reports, extract:
- Medication names, dosages, frequencies, duration

For GENERAL reports, extract:
- Diagnoses, procedures, observations, recommendations

Return the data in a structured JSON format with clear categories.
Report Type: {report_type}

Be precise and extract all numerical values, dates, and medical terms accurately.
"""),
            ("user", "Extract structured data from this report:\n\n{report_text}")
        ])

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    report_text=report_text[:8000],
                    report_type=report_type
                )
            )

            # Try to parse the response as JSON-like structure
            import json
            try:
                # Attempt to extract JSON from response
                content = response.content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                    structured_data = json.loads(json_str)
                else:
                    # If not JSON formatted, return as text
                    structured_data = {"extracted_text": content}
            except:
                structured_data = {"extracted_text": response.content}

            return {
                "structured_data": structured_data,
                "extraction_successful": True
            }

        except Exception as e:
            return {
                "structured_data": None,
                "extraction_successful": False,
                "error": str(e)
            }

    async def generate_report_summary(self, report_id: int, user_reports: list) -> Dict[str, Any]:
        """
        Generate a comprehensive summary across multiple reports for a user

        Args:
            report_id: Current report ID
            user_reports: List of all user's past medical reports

        Returns:
            Dict with longitudinal analysis
        """
        if not user_reports:
            return {"summary": "No previous reports to compare"}

        # Build timeline of reports
        report_timeline = []
        for report in user_reports:
            report_timeline.append({
                "date": report.get("report_date"),
                "type": report.get("report_type"),
                "key_findings": report.get("ai_analysis", {}).get("summary", "")[:200]
            })

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a medical records analyst. Analyze the patient's medical history and provide:

1. **Trends**: Identify changes over time in test results or conditions
2. **Patterns**: Note recurring symptoms or consistent findings
3. **Progress**: Assess if condition is improving, stable, or worsening
4. **Alerts**: Flag any concerning developments
5. **Recommendations**: Suggest follow-up tests or consultations

Be thorough and look for connections between different reports.
"""),
            ("user", "Analyze this patient's medical report history:\n\n{timeline}")
        ])

        try:
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    timeline=str(report_timeline)
                )
            )

            return {
                "longitudinal_analysis": response.content,
                "report_count": len(user_reports),
                "analysis_successful": True
            }

        except Exception as e:
            return {
                "longitudinal_analysis": None,
                "analysis_successful": False,
                "error": str(e)
            }

    async def compare_with_normal_ranges(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare lab test results with normal ranges

        Args:
            test_results: Dictionary of test names and values

        Returns:
            Dict with comparison results and flags
        """
        # Common normal ranges (this should be from a medical database in production)
        normal_ranges = {
            "hemoglobin": {"min": 13.5, "max": 17.5, "unit": "g/dL"},
            "wbc": {"min": 4.5, "max": 11.0, "unit": "10^3/μL"},
            "glucose": {"min": 70, "max": 100, "unit": "mg/dL"},
            "cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
            "ldl": {"min": 0, "max": 100, "unit": "mg/dL"},
            "hdl": {"min": 40, "max": 999, "unit": "mg/dL"},
            "triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
            "creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
            "alt": {"min": 7, "max": 56, "unit": "U/L"},
            "ast": {"min": 10, "max": 40, "unit": "U/L"},
        }

        comparisons = []
        for test_name, value in test_results.items():
            test_lower = test_name.lower().replace(" ", "")

            if test_lower in normal_ranges:
                range_info = normal_ranges[test_lower]
                try:
                    numeric_value = float(value)
                    status = "normal"

                    if numeric_value < range_info["min"]:
                        status = "low"
                    elif numeric_value > range_info["max"]:
                        status = "high"

                    comparisons.append({
                        "test": test_name,
                        "value": numeric_value,
                        "unit": range_info["unit"],
                        "normal_range": f"{range_info['min']}-{range_info['max']}",
                        "status": status,
                        "severity": "abnormal" if status != "normal" else "normal"
                    })
                except ValueError:
                    continue

        return {
            "comparisons": comparisons,
            "abnormal_count": len([c for c in comparisons if c["status"] != "normal"]),
            "total_tests": len(comparisons)
        }
