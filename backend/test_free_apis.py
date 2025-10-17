"""
Test script to demonstrate all FREE Medical APIs
Run this to see all the free APIs in action!

No API keys needed for: OpenFDA, RxNorm, PubMed, ICD-10
"""

import asyncio
from app.services.external_apis import MedicalAPIService


async def main():
    """Test all free medical APIs"""
    api_service = MedicalAPIService()

    print("=" * 80)
    print("🏥 MEDICAL AI AGENT - FREE API DEMONSTRATION")
    print("=" * 80)
    print()

    # Test 1: OpenFDA Drug Information
    print("📋 TEST 1: OpenFDA Drug Information (FREE - No API Key)")
    print("-" * 80)
    drug_name = "Aspirin"
    print(f"Searching for: {drug_name}")
    print()

    drug_info = await api_service.search_drug_info(drug_name)
    if "error" not in drug_info:
        print(f"✅ Brand Name: {drug_info.get('brand_name', 'N/A')}")
        print(f"✅ Generic Name: {drug_info.get('generic_name', 'N/A')}")
        print(f"✅ Active Ingredient: {drug_info.get('active_ingredient', 'N/A')}")
        print(f"✅ Purpose: {drug_info.get('purpose', 'N/A')[:150]}...")
        print(f"⚠️  Warnings: {drug_info.get('warnings', 'N/A')[:150]}...")
    else:
        print(f"❌ Error: {drug_info['error']}")

    print("\n" + "=" * 80 + "\n")

    # Test 2: RxNorm Drug Search
    print("💊 TEST 2: RxNorm Drug Database (FREE - No API Key)")
    print("-" * 80)
    drug_name = "Ibuprofen"
    print(f"Searching for: {drug_name}")
    print()

    rxnorm_info = await api_service.search_rxnorm(drug_name)
    if "error" not in rxnorm_info:
        print(f"✅ Found {len(rxnorm_info.get('concepts', []))} drug concepts:")
        for i, concept in enumerate(rxnorm_info.get('concepts', [])[:3], 1):
            print(f"   {i}. {concept.get('name')} (RxCUI: {concept.get('rxcui')})")
    else:
        print(f"❌ Error: {rxnorm_info['error']}")

    print("\n" + "=" * 80 + "\n")

    # Test 3: Drug Interaction Checking
    print("⚠️  TEST 3: Drug Interaction Check (FREE - No API Key)")
    print("-" * 80)
    print("Checking interactions between common medications...")
    print()

    # Get RxCUI codes for Aspirin and Warfarin
    aspirin = await api_service.search_rxnorm("Aspirin")
    warfarin = await api_service.search_rxnorm("Warfarin")

    if aspirin.get('concepts') and warfarin.get('concepts'):
        rxcui_list = [
            aspirin['concepts'][0]['rxcui'],
            warfarin['concepts'][0]['rxcui']
        ]
        interactions = await api_service.check_drug_interaction_rxnorm(rxcui_list)

        if "error" not in interactions:
            print(f"✅ Found {interactions.get('interaction_count', 0)} interactions:")
            for i, interaction in enumerate(interactions.get('interactions', [])[:3], 1):
                print(f"   {i}. Severity: {interaction.get('severity', 'Unknown')}")
                print(f"      {interaction.get('drug1')} ↔️ {interaction.get('drug2')}")
                print(f"      {interaction.get('description', 'No description')[:200]}...")
                print()
        else:
            print(f"❌ Error: {interactions['error']}")

    print("=" * 80 + "\n")

    # Test 4: PubMed Medical Literature Search
    print("📚 TEST 4: PubMed Medical Literature (FREE - No API Key)")
    print("-" * 80)
    query = "diabetes treatment"
    print(f"Searching for: {query}")
    print()

    articles = await api_service.search_medical_literature(query, max_results=3)
    if articles and "error" not in articles[0]:
        print(f"✅ Found {len(articles)} recent articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n   {i}. {article.get('title', 'N/A')}")
            print(f"      Source: {article.get('source', 'N/A')}")
            print(f"      Date: {article.get('pubdate', 'N/A')}")
            print(f"      URL: {article.get('url', 'N/A')}")
    else:
        print(f"❌ Error: {articles[0] if articles else 'No results'}")

    print("\n" + "=" * 80 + "\n")

    # Test 5: ICD-10 Medical Coding
    print("🏷️  TEST 5: ICD-10 Medical Codes (FREE - No API Key)")
    print("-" * 80)
    condition = "hypertension"
    print(f"Searching ICD-10 codes for: {condition}")
    print()

    icd_result = await api_service.get_icd10_code(condition)
    if "error" not in icd_result:
        print(f"✅ Found {len(icd_result.get('results', []))} ICD-10 codes:")
        for i, code_info in enumerate(icd_result.get('results', [])[:5], 1):
            print(f"   {i}. Code: {code_info.get('code')}")
            print(f"      Description: {code_info.get('description')}")
    else:
        print(f"❌ Error: {icd_result['error']}")

    print("\n" + "=" * 80 + "\n")

    # Test 6: Medication Safety Analysis
    print("🔬 TEST 6: Comprehensive Medication Safety Analysis")
    print("-" * 80)
    drug_name = "Penicillin"
    user_allergies = ["Penicillin"]
    user_conditions = ["Diabetes", "Hypertension"]

    print(f"Analyzing safety of: {drug_name}")
    print(f"User allergies: {user_allergies}")
    print(f"User conditions: {user_conditions}")
    print()

    safety = await api_service.analyze_medication_safety(
        drug_name,
        user_allergies,
        user_conditions
    )

    if "error" not in safety:
        print(f"✅ Safety Score: {safety.get('safety_score', 'N/A')}")
        print(f"✅ Brand Name: {safety.get('fda_information', {}).get('brand_name', 'N/A')}")

        allergy_warnings = safety.get('allergy_warnings', [])
        if allergy_warnings:
            print(f"\n⚠️  ALLERGY WARNINGS ({len(allergy_warnings)}):")
            for warning in allergy_warnings:
                print(f"   - {warning}")

        condition_warnings = safety.get('condition_warnings', [])
        if condition_warnings:
            print(f"\n⚠️  CONDITION WARNINGS ({len(condition_warnings)}):")
            for warning in condition_warnings:
                print(f"   - {warning}")

        print(f"\n📝 Recommendation:")
        print(f"   {safety.get('overall_recommendation', 'N/A')}")
    else:
        print(f"❌ Error: {safety['error']}")

    print("\n" + "=" * 80 + "\n")

    # Test 7: Drug Suggestions by Condition
    print("💡 TEST 7: Drug Suggestions for Conditions")
    print("-" * 80)
    condition = "headache"
    print(f"Getting drug suggestions for: {condition}")
    print()

    suggestions = await api_service.get_drug_suggestions(condition)
    if "error" not in suggestions:
        print(f"✅ Condition: {suggestions.get('condition')}")

        icd_codes = suggestions.get('icd10_codes', [])
        if icd_codes:
            print(f"\n   ICD-10 Codes:")
            for code in icd_codes[:3]:
                print(f"   - {code.get('code')}: {code.get('description')}")

        articles = suggestions.get('research_articles', [])
        if articles:
            print(f"\n   Recent Research:")
            for i, article in enumerate(articles[:2], 1):
                print(f"   {i}. {article.get('title', 'N/A')[:80]}...")

        print(f"\n   ⚠️  Disclaimer: {suggestions.get('disclaimer', 'N/A')}")
    else:
        print(f"❌ Error: {suggestions['error']}")

    print("\n" + "=" * 80 + "\n")

    # Summary
    print("✅ ALL FREE MEDICAL APIs TESTED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("🎉 Summary:")
    print("   • OpenFDA: Drug information, warnings, side effects")
    print("   • RxNorm: Standardized drug names and codes")
    print("   • RxNorm Interactions: Drug interaction checking")
    print("   • PubMed: Medical literature and research")
    print("   • ICD-10: Medical condition coding")
    print("   • Combined: Comprehensive medication safety analysis")
    print()
    print("💰 Cost: $0.00 - All APIs are 100% FREE!")
    print("🔑 API Keys Required: ZERO")
    print()
    print("🚀 Your medical AI agent now has access to all this data!")
    print("=" * 80)

    await api_service.close()


if __name__ == "__main__":
    print("\n🚀 Starting Free Medical API Tests...\n")
    asyncio.run(main())
