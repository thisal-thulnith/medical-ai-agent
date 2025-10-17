"""
Integration with free external medical APIs
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings


class MedicalAPIService:
    """
    Service to interact with free medical APIs:
    - OpenFDA: Drug information
    - PubMed: Medical research articles
    - USDA FoodData: Nutritional information
    """

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_drug_info(self, drug_name: str) -> Dict[str, Any]:
        """
        Search drug information using OpenFDA API (FREE, no key needed)

        API Docs: https://open.fda.gov/apis/drug/

        Args:
            drug_name: Name of the drug

        Returns:
            Dict with drug information
        """
        try:
            url = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f'openfda.brand_name:"{drug_name}" OR openfda.generic_name:"{drug_name}"',
                "limit": 1
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                return {
                    "brand_name": result.get("openfda", {}).get("brand_name", ["Unknown"])[0],
                    "generic_name": result.get("openfda", {}).get("generic_name", ["Unknown"])[0],
                    "purpose": result.get("purpose", ["No purpose information"])[0] if result.get("purpose") else "No purpose information",
                    "warnings": result.get("warnings", ["No warnings available"])[0] if result.get("warnings") else "No warnings available",
                    "active_ingredient": result.get("active_ingredient", ["Unknown"])[0] if result.get("active_ingredient") else "Unknown",
                    "dosage_and_administration": result.get("dosage_and_administration", ["No dosage information"])[0] if result.get("dosage_and_administration") else "No dosage information",
                    "adverse_reactions": result.get("adverse_reactions", ["No adverse reaction information"])[0] if result.get("adverse_reactions") else "No adverse reaction information",
                }
            else:
                return {"error": "Drug not found"}

        except Exception as e:
            return {"error": str(e)}

    async def check_drug_interactions(self, drug_name: str) -> Dict[str, Any]:
        """
        Check for drug interaction information

        Args:
            drug_name: Name of the drug

        Returns:
            Dict with interaction warnings
        """
        try:
            url = "https://api.fda.gov/drug/label.json"
            params = {
                "search": f'openfda.brand_name:"{drug_name}" AND drug_interactions',
                "limit": 1
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                return {
                    "drug_name": drug_name,
                    "interactions": result.get("drug_interactions", ["No interaction information available"])[0] if result.get("drug_interactions") else "No interaction information available"
                }
            else:
                return {"error": "No interaction information found"}

        except Exception as e:
            return {"error": str(e)}

    async def search_medical_literature(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search PubMed for medical research articles (FREE, no key needed)

        API Docs: https://www.ncbi.nlm.nih.gov/home/develop/api/

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List of article summaries
        """
        try:
            # Step 1: Search for article IDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json"
            }

            search_response = await self.client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            article_ids = search_data.get("esearchresult", {}).get("idlist", [])

            if not article_ids:
                return []

            # Step 2: Fetch article summaries
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(article_ids),
                "retmode": "json"
            }

            summary_response = await self.client.get(summary_url, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()

            articles = []
            for article_id in article_ids:
                article_info = summary_data.get("result", {}).get(article_id, {})
                articles.append({
                    "pmid": article_id,
                    "title": article_info.get("title", "No title"),
                    "authors": article_info.get("authors", []),
                    "source": article_info.get("source", "Unknown"),
                    "pubdate": article_info.get("pubdate", "Unknown"),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{article_id}/"
                })

            return articles

        except Exception as e:
            return [{"error": str(e)}]

    async def get_nutrition_info(self, food_name: str) -> Dict[str, Any]:
        """
        Get nutritional information using USDA FoodData API

        API Docs: https://fdc.nal.usda.gov/api-guide.html
        Get free API key: https://fdc.nal.usda.gov/api-key-signup.html

        Args:
            food_name: Name of the food

        Returns:
            Dict with nutritional information
        """
        if not settings.USDA_API_KEY:
            return {"error": "USDA API key not configured"}

        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "api_key": settings.USDA_API_KEY,
                "query": food_name,
                "pageSize": 1
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("foods"):
                food = data["foods"][0]
                nutrients = {}

                for nutrient in food.get("foodNutrients", []):
                    nutrient_name = nutrient.get("nutrientName")
                    nutrient_value = nutrient.get("value")
                    nutrient_unit = nutrient.get("unitName")

                    if nutrient_name and nutrient_value:
                        nutrients[nutrient_name] = f"{nutrient_value} {nutrient_unit}"

                return {
                    "food_name": food.get("description"),
                    "brand": food.get("brandOwner", "Generic"),
                    "nutrients": nutrients,
                    "serving_size": food.get("servingSize"),
                    "serving_unit": food.get("servingSizeUnit")
                }
            else:
                return {"error": "Food not found"}

        except Exception as e:
            return {"error": str(e)}

    async def get_icd10_code(self, condition_name: str) -> Dict[str, Any]:
        """
        Search for ICD-10 codes for medical conditions

        Note: For a free ICD-10 API, you can use:
        - https://clinicaltables.nlm.nih.gov/ (FREE, no key)

        Args:
            condition_name: Medical condition name

        Returns:
            Dict with ICD-10 code and description
        """
        try:
            url = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"
            params = {
                "sf": "code,name",
                "terms": condition_name,
                "maxList": 5
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if len(data) > 3 and data[3]:
                results = []
                for item in data[3]:
                    results.append({
                        "code": item[0],
                        "description": item[1]
                    })
                return {"results": results}
            else:
                return {"error": "No ICD-10 codes found"}

        except Exception as e:
            return {"error": str(e)}

    async def search_rxnorm(self, drug_name: str) -> Dict[str, Any]:
        """
        Search for drug information using RxNorm API (FREE, no key needed)

        RxNorm provides standard drug names and drug interaction checking.
        API Docs: https://rxnav.nlm.nih.gov/

        Args:
            drug_name: Name of the drug

        Returns:
            Dict with RxNorm drug information
        """
        try:
            # Search for drug concept
            search_url = "https://rxnav.nlm.nih.gov/REST/drugs.json"
            search_params = {"name": drug_name}

            response = await self.client.get(search_url, params=search_params)
            response.raise_for_status()
            data = response.json()

            if data.get("drugGroup", {}).get("conceptGroup"):
                concepts = []
                for group in data["drugGroup"]["conceptGroup"]:
                    if group.get("conceptProperties"):
                        for concept in group["conceptProperties"]:
                            concepts.append({
                                "rxcui": concept.get("rxcui"),
                                "name": concept.get("name"),
                                "synonym": concept.get("synonym"),
                                "tty": concept.get("tty")  # Term type
                            })

                return {
                    "drug_name": drug_name,
                    "concepts": concepts[:5]  # Limit to top 5
                }
            else:
                return {"error": "Drug not found in RxNorm"}

        except Exception as e:
            return {"error": str(e)}

    async def check_drug_interaction_rxnorm(self, rxcui_list: List[str]) -> Dict[str, Any]:
        """
        Check drug interactions using RxNorm Interaction API (FREE)

        Args:
            rxcui_list: List of RxCUI identifiers for drugs

        Returns:
            Dict with drug interaction information
        """
        try:
            # RxNorm interaction API
            url = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"
            params = {"rxcuis": "+".join(rxcui_list)}

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            interactions = []
            if data.get("fullInteractionTypeGroup"):
                for type_group in data["fullInteractionTypeGroup"]:
                    for interaction_type in type_group.get("fullInteractionType", []):
                        for interaction in interaction_type.get("interactionPair", []):
                            interactions.append({
                                "severity": interaction.get("severity", "Unknown"),
                                "description": interaction.get("description", "No description"),
                                "drug1": interaction["interactionConcept"][0].get("minConceptItem", {}).get("name"),
                                "drug2": interaction["interactionConcept"][1].get("minConceptItem", {}).get("name")
                            })

            return {
                "interaction_count": len(interactions),
                "interactions": interactions
            }

        except Exception as e:
            return {"error": str(e)}

    async def get_drug_suggestions(self, symptom_or_condition: str) -> Dict[str, Any]:
        """
        Get drug suggestions based on symptoms or conditions
        Uses combination of multiple APIs

        Args:
            symptom_or_condition: Medical symptom or condition

        Returns:
            Dict with suggested medications and information
        """
        try:
            # First, get ICD-10 code for the condition
            icd_result = await self.get_icd10_code(symptom_or_condition)

            # Search medical literature for treatment options
            literature = await self.search_medical_literature(
                f"{symptom_or_condition} treatment medication",
                max_results=3
            )

            return {
                "condition": symptom_or_condition,
                "icd10_codes": icd_result.get("results", [])[:3],
                "research_articles": literature,
                "disclaimer": "This is informational only. Always consult a healthcare provider before taking any medication."
            }

        except Exception as e:
            return {"error": str(e)}

    async def analyze_medication_safety(self, drug_name: str, user_allergies: List[str], user_conditions: List[str]) -> Dict[str, Any]:
        """
        Comprehensive medication safety analysis

        Args:
            drug_name: Name of the medication to analyze
            user_allergies: List of user's allergies
            user_conditions: List of user's medical conditions

        Returns:
            Dict with comprehensive safety analysis
        """
        try:
            # Get drug information from OpenFDA
            fda_info = await self.search_drug_info(drug_name)

            # Get RxNorm information
            rxnorm_info = await self.search_rxnorm(drug_name)

            # Check for interactions
            interaction_info = await self.check_drug_interactions(drug_name)

            # Analyze allergies
            allergy_warnings = []
            if fda_info.get("active_ingredient"):
                active_ingredient = fda_info["active_ingredient"].lower()
                for allergy in user_allergies:
                    if allergy.lower() in active_ingredient:
                        allergy_warnings.append(f"WARNING: Active ingredient may contain {allergy}")

            # Analyze contraindications with user conditions
            condition_warnings = []
            warnings_text = fda_info.get("warnings", "").lower()
            for condition in user_conditions:
                if condition.lower() in warnings_text:
                    condition_warnings.append(f"CAUTION: May have contraindications with {condition}")

            return {
                "drug_name": drug_name,
                "safety_score": self._calculate_safety_score(allergy_warnings, condition_warnings),
                "fda_information": {
                    "brand_name": fda_info.get("brand_name"),
                    "generic_name": fda_info.get("generic_name"),
                    "purpose": fda_info.get("purpose"),
                    "active_ingredient": fda_info.get("active_ingredient")
                },
                "allergy_warnings": allergy_warnings,
                "condition_warnings": condition_warnings,
                "interaction_warnings": interaction_info.get("interactions", "No known interactions"),
                "adverse_reactions": fda_info.get("adverse_reactions"),
                "dosage_information": fda_info.get("dosage_and_administration"),
                "rxnorm_data": rxnorm_info,
                "overall_recommendation": self._generate_recommendation(allergy_warnings, condition_warnings)
            }

        except Exception as e:
            return {"error": str(e)}

    def _calculate_safety_score(self, allergy_warnings: List[str], condition_warnings: List[str]) -> str:
        """Calculate a simple safety score"""
        total_warnings = len(allergy_warnings) + len(condition_warnings)

        if total_warnings == 0:
            return "SAFE"
        elif total_warnings <= 2:
            return "CAUTION"
        else:
            return "HIGH_RISK"

    def _generate_recommendation(self, allergy_warnings: List[str], condition_warnings: List[str]) -> str:
        """Generate overall recommendation"""
        if allergy_warnings:
            return "⚠️ DO NOT TAKE - Potential allergy risk. Consult your doctor immediately."
        elif condition_warnings:
            return "⚠️ CAUTION - May interact with your medical conditions. Consult your doctor before use."
        else:
            return "✅ No immediate contraindications found, but always consult your healthcare provider."

    async def extract_text_from_image(self, file_path: str = None, file_url: str = None) -> Dict[str, Any]:
        """
        Extract text from medical report images using FREE OCR.space API

        OCR.space is a FREE OCR API (no registration required)
        - API Docs: https://ocr.space/ocrapi
        - Free tier: 25,000 requests/month
        - No API key needed for basic usage

        Args:
            file_path: Local path to image file (PDF, JPG, PNG)
            file_url: URL to image file (alternative to file_path)

        Returns:
            Dict with extracted text and metadata
        """
        try:
            url = "https://api.ocr.space/parse/image"

            # OCR.space free API endpoint
            headers = {
                "apikey": "helloworld"  # Free API key that works without registration
            }

            data = {
                "language": "eng",
                "isOverlayRequired": False,
                "detectOrientation": True,
                "scale": True,
                "OCREngine": 2  # Engine 2 is better for medical documents
            }

            if file_path:
                # Upload from file
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = await self.client.post(url, headers=headers, data=data, files=files)
            elif file_url:
                # Process from URL
                data['url'] = file_url
                response = await self.client.post(url, headers=headers, data=data)
            else:
                return {"error": "Either file_path or file_url must be provided"}

            response.raise_for_status()
            result = response.json()

            if result.get("IsErroredOnProcessing"):
                return {
                    "error": result.get("ErrorMessage", ["Unknown error"])[0] if result.get("ErrorMessage") else "OCR processing failed",
                    "raw_response": result
                }

            # Extract text from parsed results
            extracted_text = ""
            if result.get("ParsedResults"):
                for page in result["ParsedResults"]:
                    extracted_text += page.get("ParsedText", "") + "\n"

            return {
                "success": True,
                "extracted_text": extracted_text.strip(),
                "confidence": result.get("ParsedResults", [{}])[0].get("FileParseExitCode", 0),
                "processing_time": result.get("ProcessingTimeInMilliseconds", 0),
                "raw_response": result
            }

        except Exception as e:
            return {
                "error": f"OCR extraction failed: {str(e)}",
                "success": False
            }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
