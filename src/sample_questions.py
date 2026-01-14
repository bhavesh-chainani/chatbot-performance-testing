"""
Sample Questions for Chatbot Testing
Easy-to-edit file containing all test questions organized by category

To add or modify questions, simply edit the lists below.
The weights at the bottom control how frequently each category appears.
"""

# ============================================================================
# Simple Questions
# Fast responses expected - basic trade and certificate questions
# ============================================================================
SIMPLE_MESSAGES = [
    "What is a Certificate of Origin?",
    "What does PCO stand for?",
    "What is an HS code?",
    "What is an FTA?",
    "What countries have FTAs with Singapore?",
    "How do I contact SBF for trade advice?",
    "What is a tariff?",
    "What is customs clearance?",
    "What is ASEAN?",
    "What documents are needed for exporting?",
    "What is a commercial invoice?",
    "What is a packing list?",
    "What is a bill of lading?",
    "What is the difference between FOB and CIF?",
    "What is a letter of credit?",
]

# ============================================================================
# Common Questions
# Moderate complexity - Typical trade and certificate queries
# ============================================================================
COMMON_QUESTIONS = [
    "Check requirements for Back-to-back Preferential Certificate of Origin (PCO)",
    "Check product eligibility for Free Trade Agreements (FTA) and Preferential Tariffs",
    "Check the eligibility criteria for Ordinary Certificate of Origin (OCO)",
    "What documents do I need for a Certificate of Origin?",
    "How do I apply for a Preferential Certificate of Origin?",
    "What is the difference between PCO and OCO?",
    "Which Free Trade Agreements does Singapore have?",
    "How long does it take to process a Certificate of Origin?",
    "What are the requirements for FTA eligibility?",
    "Can I check if my product qualifies for preferential tariffs?",
    "What is a Back-to-back Certificate of Origin?",
    "How do I verify my product's origin?",
    "What are the fees for certificate applications?",
    "Where can I submit my certificate application?",
    "What information is required for FTA verification?",
    "How do I apply for a PCO in Singapore?",
    "What are the requirements for a Back-to-Back PCO?",
    "How do I determine the correct HS code for my product?",
    "How do I calculate Regional Value Content (RVC)?",
    "What documents are required for exporting to China?",
    "How long does it take to process a PCO application?",
    "What are the fees for PCO applications?",
    "How do I verify if my product qualifies for preferential tariff treatment?",
    "What are the rules of origin under the ASEAN FTA?",
    "How do I handle transhipment of goods through Singapore?",
    "What are the customs procedures for importing goods into Singapore?",
    "How do I prepare a Manufacturing Cost Statement?",
    "What are the common mistakes in PCO applications?",
    "How do I amend an issued PCO?",
    "What are the compliance requirements for exporting to the EU?",
]

# ============================================================================
# Complex Questions
# Detailed multi-part queries that may take longer to process
# ============================================================================
COMPLEX_QUESTIONS = [
    "I'm exporting electronics to multiple ASEAN countries. Can you explain the complete process for obtaining Preferential Certificates of Origin for each country, including the specific requirements, documentation needed, and how to verify product eligibility under different FTAs?",
    "I need to understand the full eligibility criteria for Back-to-back Preferential Certificate of Origin. Can you provide detailed information about the requirements, application process, supporting documents needed, processing time, and any common issues that might cause rejection?",
    "My company manufactures products using components from multiple countries. How do I determine the origin of my finished product for FTA purposes, what documentation is required to prove origin, and which Free Trade Agreements would provide the best tariff benefits for my specific product category?",
    "I'm new to international trade and need comprehensive guidance. Can you explain the differences between Ordinary Certificate of Origin and Preferential Certificate of Origin, when to use each, the application procedures, required documents, processing timelines, and how to check product eligibility for preferential tariffs under various FTAs?",
    "I have a shipment ready to export but I'm unsure about certificate requirements. Can you help me determine which type of certificate I need, verify my product's eligibility for preferential treatment, guide me through the complete application process including all required documents, and explain how to avoid common mistakes that could delay or reject my application?",
    "How do I determine substantial transformation for goods processed in Singapore for a Back-to-Back PCO?",
    "What are the specific origin criteria differences between ASEAN-China FTA and RCEP for electronic components?",
    "How do I handle cumulation of origin across multiple countries under RCEP?",
    "What are the implications of third-country invoicing on PCO eligibility?",
    "How do I navigate conflicting rules of origin between overlapping FTAs?",
    "What strategies can I use to optimize tariff benefits across multiple FTAs?",
    "How do I handle partial shipments with a single PCO?",
    "What are the legal implications of incorrect origin declarations?",
    "How do I manage product-specific rules vs. general rules for complex manufactured goods?",
    "What documentation is required for proving origin when components come from multiple countries?",
    "How do I handle retroactive issuance of PCOs for shipments already in transit?",
    "What are the verification procedures if my PCO is challenged by foreign customs?",
    "How do I calculate regional value content for products with components from multiple FTA partners?",
    "What are the implications of minimal operations provisions on my manufacturing process?",
    "How do I handle origin certification for goods that undergo processing in multiple countries?",
]

# ============================================================================
# Question Distribution Weights
# ============================================================================
# These weights control how frequently each category appears in the test
# Higher weight = more frequent appearance
# 
# Example: If SIMPLE_WEIGHT=2, COMMON_WEIGHT=3, COMPLEX_WEIGHT=1
# Then for every 6 questions, you'll get:
# - 2 simple messages
# - 3 common questions  
# - 1 complex question
# ============================================================================
SIMPLE_WEIGHT = 1      # Simple messages
COMMON_WEIGHT = 4      # Common questions
COMPLEX_WEIGHT = 5     # Complex questions

# ============================================================================
# Combined Sample Messages
# ============================================================================
# This combines all questions with their weights applied
# You typically don't need to modify this - it's calculated automatically
# ============================================================================
def get_sample_messages():
    """Get combined sample messages with weights applied"""
    return (
        SIMPLE_MESSAGES * SIMPLE_WEIGHT +
        COMMON_QUESTIONS * COMMON_WEIGHT +
        COMPLEX_QUESTIONS * COMPLEX_WEIGHT
    )

# ============================================================================
# Question Category Helper
# ============================================================================
def get_question_category(message):
    """
    Determine the category of a question for TTF tracking
    
    Args:
        message: The question text
        
    Returns:
        str: Category name ("Simple", "Common", "Complex", or "Unknown")
    """
    if message in SIMPLE_MESSAGES:
        return "Simple"
    elif message in COMMON_QUESTIONS:
        return "Common"
    elif message in COMPLEX_QUESTIONS:
        return "Complex"
    else:
        return "Unknown"
