"""
Sample Questions for Chatbot Testing
Easy-to-edit file containing all test questions organized by category

To add or modify questions, simply edit the lists below.
The weights at the bottom control how frequently each category appears.
"""

# ============================================================================
# Simple/Greeting Messages
# Fast responses expected - basic interactions
# ============================================================================
SIMPLE_MESSAGES = [
    "Hello",
    "Hi",
    "Good morning",
    "What can you help me with?",
    "Thank you",
    "Thanks",
    "I need help",
    "Can you assist me?",
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
SIMPLE_WEIGHT = 0      # Simple messages
COMMON_WEIGHT = 1      # Common questions
COMPLEX_WEIGHT = 1     # Complex questions

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

