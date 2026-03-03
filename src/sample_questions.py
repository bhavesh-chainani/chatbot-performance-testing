"""
Sample Questions for Chatbot Testing
Easy-to-edit file containing all test questions organized by category

To add or modify questions, simply edit the lists below.
The weights at the bottom control how frequently each category appears.
"""

# ============================================================================
# Direct Questions
# Fast responses expected - basic trade and certificate questions
# ============================================================================
DIRECT_QUESTIONS = [
    "Which Free Trade Agreements (FTAs) can I utilise when exporting umbrellas (HS Code: 6601.99.00.03) from Singapore to Australia?",
    "I am importing blowers under 125kW from China to Singapore. I don't know the HS code of my product. Could you provide some suggestions?",
    "We are a manufacturing company looking to export plastic bottles to customers in other countries. Can you please advise the steps and processes we have to take?",
    "I would like to export beet sugar with HS code 1701.12 from Singapore to either Laos or New Zealand. What FTAs can I leverage?",
    "My company manufactures porcelain cups in Singapore and sells them to customers in the Philippines. I would like to find out more about FTAs and whether they can help me in my exports.",
    "I would like to export my product of HS 4819.60 from Singapore to India. What is the duty rate and what FTAs can I leverage?",
    "Could you help me identify if my product with HS code 4415.10.01 is eligible for tariff concessions for export to Mexico from Singapore?",
    "I would like to know more about the import duties for export from Singapore to US. HS code for my product is 9404.21.00.10. Estimated export value for each mattress is $150.",
    "I am exporting meat with HS code 0210.19.90 from Singapore to Indonesia. The export value is 10,000 SGD. Which FTAs can I leverage?",
    "Please provide guidance on enjoying FTA tariffs benefit for the export of S$100,000 worth of electric motors (HS code: 8501.10.10.30) from Singapore to the United Kingdom.",
    "I am exporting T-Shirt with HS code 6109.10.10 from Singapore to Thailand. What FTAs would be beneficial for my export?",
    "I have an energy product with HS code 2710.12.15.10 that is made in Canada and to be exported to the US. My goods do not meet the rules of origin under the USMCA. What is the tariff?",
    "Are there any tariffs for the import of fresh apples with HS code 0808.10.00.45 into the US from Canada?",
    "My company exports an energy resource with HS code 2710.12.18.05 from Mexico to the US, will there be additional tariffs?",
    "I am exporting 1001.19.00.25 from Singapore to the US. Are there any additional tariffs?",
    "I am exporting 3305.20 from Japan to the US. Are there any additional tariffs?",
    "What tariff will my aluminium rods with HS code 7604.29.10.10 be subject to if it was manufactured in Russia and exported to the US?",
    "I am importing iron pipes with HS code 7303.00.00.30 from Malaysia to the US. What are the additional tariffs that apply?",
    "I am exporting umbrella parts with HS code 6603.90.41 from Brazil to the US. What are the additional tariffs?",
    "I am exporting propulsion engines with HS code 8408.10.00.05 from Germany to the US. What tariffs apply?",
    "I am an automobile manufacturer importing parts of a suspension system with HS code 8708.80.55 from Germany which will be assembled in the US. Am I eligible for lower tariffs?",
    "I am exporting steel forgings of gear boxes with HS code 8708.40.75.70 from China to the US. What tariffs apply?",
    "I am exporting fruits with HS code 0811.10.00.50 from Thailand to the US. What tariffs apply?",
    "I am exporting salmon with HS code 0303.11 from Norway to the US. What tariffs apply?",
    "I am exporting essential oils with HS code 3301.29.51.03 from France to the US. What tariffs apply?",
    "I am exporting t-shirts with HS code 6109.10.00.14 from Colombia to the US. What tariffs apply?",
    "What is the validity period of back-to-back COs issued by Singapore Customs, and can validity be extended?",
    "Can we issue a back-to-back PCO when the import CO was issued under a different FTA than the export FTA?",
    "What's the practical difference between RVC build-up and build-down methods and when is each preferable?",
    "What are the consequences and corrective actions if I inadvertently use an incorrect HS code on a Certificate of Origin?",
    "How do I identify appropriate HS codes and market requirements for exporting headphones to the Philippines?",
    "What is Singapore Customs' approach to border controls against counterfeit goods?",
    "How many FTAs has Singapore signed versus those currently in force, and where can I verify the latest status?",
    "Can a non-preferential Certificate of Origin be issued after shipment, and what evidence is required?",
    "Which agreements used by Singapore allow exporter self-certification, and what are the eligibility conditions?",
    "How do I calculate RVC for a plastic household item under ATIGA and document it for possible verification?",
    "When forming a Japan–Singapore joint-venture apparel retailer, which FTAs, domestic laws, and compliance obligations need to be taken into account?",
    "What is the process to revise or correct a Manufacturing Cost Statement that has already been submitted?",
    "In what ways do digital trade provisions in relevant agreements create sector-specific opportunities and advantages, and how do they improve market access and cross-border dealings?",
    "Which official sources provide documentation or certification showing that companies from certain countries are eligible to participate in Singapore government procurement under specific agreements?",
    "If software classified as strategic goods technology is hosted on a server in Singapore for global download, what authorisations are required under Singapore's Strategic Goods (Control) regime?",
    "Where do I access certified lists or notices indicating country eligibility for Singapore public tenders under certain agreements?",
    "What is the authoritative source for eligibility criteria and certifications for foreign suppliers in Singapore government procurement under specified agreements?",
    # More direct – single product/route/concept
    "What FTAs can I use to export coffee (HS 0901.21) from Singapore to Chile?",
    "I export wooden furniture (HS 9403.60) from Singapore to Australia. What is the duty rate under the relevant FTA?",
    "Which FTA gives the best tariff for exporting solar panels (HS 8541.40) from Singapore to Japan?",
    "What is the tariff for importing stainless steel sheets (HS 7219.13) from Indonesia into Singapore under ATIGA?",
    "I want to export medicinal herbs (HS 1211.90) from Singapore to the EU. Which agreement applies?",
    "What documents do I need to apply for a Preferential Certificate of Origin under RCEP for export to China?",
    "How long does it take to get a PCO from Singapore Customs for ATIGA export to Thailand?",
    "Can I use the UK-Singapore FTA for exporting machinery parts (HS 8483.40) to the United Kingdom?",
    "What is the difference between a Certificate of Origin and a Preferential Certificate of Origin?",
    "Where can I find the rules of origin for my product under the Singapore-Australia FTA?",
    "I am exporting rubber gloves (HS 4015.19) from Singapore to Malaysia. Which FTA applies?",
    "What is the tariff rate for exporting printed books (HS 4901.99) from Singapore to Vietnam under ATIGA?",
    "Does Singapore have an FTA with Turkey? If yes, what is the tariff for exporting textiles (HS 5407)?",
    "What is an Ordinary Certificate of Origin and when do I need it?",
    "I export seafood (HS 0304) from Singapore to South Korea. What FTA and duty rate apply?",
    "How do I check if my product qualifies for zero tariff under RCEP?",
    "What is the validity period of a PCO issued under ATIGA?",
    "Can a Singapore company apply for a PCO for goods manufactured in Malaysia and exported to Indonesia?",
    "What HS code should I use for LED light fixtures (ceiling type) for export to India?",
    "I am importing ceramic tiles (HS 6908.90) from Vietnam to Singapore. What tariff applies under ATIGA?",
    "Which Singapore FTA covers trade in services, not just goods?",
    "What is SBF's role in trade documentation and FTA support for Singapore businesses?",
    "Where do I get help with FTA and Certificate of Origin queries in Singapore?",
]

# ============================================================================
# Indirect Questions
# Detailed multi-part queries that may take longer to process
# ============================================================================
INDIRECT_QUESTIONS = [
    "Which Free Trade Agreements (FTAs) can I utilise when exporting compact disks (HS Code: 8523.41.10) from Singapore to Indonesia?",
    "What is the PCO application process for the export of my product with HS code 3924.90.90 from Singapore to Vietnam with an estimated export value of 5,000 SGD under the ATIGA FTA?",
    "I would like to leverage the AKFTA FTA for my export of 1701.12.20 from Singapore to South Korea. What is a PCO and how do I apply for it?",
    "How do I qualify for preferential treatment under the ATIGA for my export of water pumps with HS code 8413.20.90 from Singapore to Indonesia?",
    "We import fresh mangoes (HS 0804.50) from Indonesia into Singapore and plan to re-export them to the Philippines. Can we request a back-to-back PCO under ATIGA?",
    "We import Korean cosmetics (HS 3304) under RCEP into Singapore and re-export to Japan with no further processing. Can we apply for a back-to-back RCEP certificate?",
    "Can we ship goods directly from China to Indonesia with a Singapore invoice and still claim ACFTA preference?",
    "We assemble vacuum cleaners (HS Code 8508.19.10) in Singapore from Chinese parts and export to Indonesia. Does simple assembly confer Singapore origin, or should we apply for a back-to-back PCO instead?",
    "We import headphones (HS 8518.30.10) from China and sell to Vietnam. Can CPTPP preferences ever apply, and what proof would be required?",
    "For shipments from Singapore to Australia with goods sourced from Japan and Korea, what are the steps to claim AANZFTA or RCEP preferences?",
    "Under which FTAs, if any, can India-origin goods use a back-to-back mechanism via Singapore?",
    "If I import products from South Korea into Singapore, store them in Singapore, and then export them to Vietnam. Is there any FTA I can use to obtain duty savings on import into Vietnam?",
    "I import machinery parts from Japan to Singapore and would like to re-export to India. The HS code of the machinery parts are 8401.10. Am I eligible for any FTAs?",
    "I import brooms with HS code 9603.10.20 from China to Singapore and would like to re-export to Malaysia. Am I eligible for any FTAs?",
    "I import meat with HS code 0201.30.01 from Australia to Singapore and re-export to Japan. Am I eligible for preferential tariffs?",
    "We plan to bring microprocessors (HS 8542.31) from Japan into Singapore for consolidation, then ship them to Indonesia. Can we claim preferential tariff treatment on the Indonesia leg?",
    "I want to import semiconductor integrated circuits from South Korea to Singapore and intend to re-export them to Vietnam. The HS code is 8542.31. Am I eligible for any FTAs?",
    # More indirect – multi-part, re-export, origin rules
    "We import cotton fabric (HS 5208) from India into Singapore, dye and cut it here, then export garments to the EU. How do we determine origin under RCEP and EU-Singapore FTA, and what documentation do we need for both legs?",
    "Our company sources components from China, Thailand, and Malaysia and assembles electronic switches (HS 8536.50) in Singapore for export to Australia. Can we claim Singapore origin under AANZFTA, and what RVC method and supporting documents are required?",
    "We have a back-to-back PCO under RCEP for goods from Japan. The buyer in Indonesia wants to split the shipment into two consignments over two months. Is the original PCO still valid, and what do we need to do for the second shipment?",
    "If we import under ASEAN-China FTA and re-export to Japan under RCEP with minimal repackaging in Singapore, can we use a back-to-back certificate, and what are the conditions and time limits?",
    "We manufacture plastic containers (HS 3924) in Singapore using resin from Saudi Arabia and additives from Malaysia. How do we prove origin under ATIGA for export to Vietnam, and which FTA gives the better tariff?",
    "Our goods qualify under both RCEP and ATIGA for export to Thailand. Which agreement should we use for the PCO, and does it affect how we complete the origin declaration?",
    "We import wine (HS 2204) from Australia under the Singapore-Australia FTA and store it in a bonded warehouse. When we re-export to Japan, can we claim preference under RCEP or CPTPP, and what evidence is needed?",
    "For machinery (HS 8479) assembled in Singapore from US and German parts, what are the rules of origin under the EU-Singapore FTA and UK-Singapore FTA, and how do we calculate and document RVC?",
    "We ship from Singapore to multiple ASEAN countries (Indonesia, Philippines, Vietnam) under ATIGA. Do we need one PCO per destination or one for the whole order, and what are the declaration requirements for each?",
    "We received a request from Indonesian customs to verify our ATIGA PCO. What is the process for Singapore exporters, what documents must we provide, and what is the typical timeline?",
    "We are considering moving some production from China to Singapore to benefit from FTAs. For electronics (HS 8517), what origin criteria apply under RCEP and CPTPP, and what percentage of value must be added in Singapore?",
    "We import raw cocoa (HS 1801) from Ghana, process it into chocolate (HS 1806) in Singapore, and export to Japan. How do we prove substantial transformation and claim preference under RCEP?",
    "Can we use exporter self-certification under the UK-Singapore FTA for our exports of pharmaceutical products (HS 3004), and what are the exact conditions and record-keeping requirements?",
    "We have an existing PCO but the importer says the HS code on the certificate does not match their customs declaration. How do we correct or reissue the certificate, and will it affect the validity period?",
    "For goods that qualify under both ATIGA and RCEP when exporting from Singapore to Thailand, how do we choose which FTA to use, and can we switch between them for different shipments of the same product?",
    "We consolidate shipments from multiple ASEAN countries in Singapore and then send them to Australia. Can we obtain a single certificate covering the whole consignment, or do we need separate origin documentation for each origin country?",
    "What are the steps and timelines to apply for a PCO under the Digital Economy Agreement between Singapore and Australia, and how does it differ from the standard goods FTA process?",
    "We export organic fertiliser (HS 3101) from Singapore to New Zealand. Under CPTPP, what are the rules of origin and any product-specific requirements we must meet?",
    "If our PCO application is rejected by Singapore Customs due to insufficient supporting documents, what can we do to rectify and reapply, and how long does the appeal or correction process take?",
]

# ============================================================================
# Question Distribution Weights
# ============================================================================
# These weights control how frequently each category appears in the test
# Higher weight = more frequent appearance
#
# Example: If DIRECT_WEIGHT=1, INDIRECT_WEIGHT=3
# Then for every 4 questions, you'll get:
# - 1 direct question
# - 3 indirect questions
# ============================================================================
DIRECT_WEIGHT = 2      # Direct questions
INDIRECT_WEIGHT = 8    # Indirect questions

# ============================================================================
# Combined Sample Messages
# ============================================================================
# This combines all questions with their weights applied
# You typically don't need to modify this - it's calculated automatically
# ============================================================================
def get_sample_messages():
    """Get combined sample messages with weights applied"""
    return (
        DIRECT_QUESTIONS * DIRECT_WEIGHT +
        INDIRECT_QUESTIONS * INDIRECT_WEIGHT
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
        str: Category name ("Direct", "Indirect", or "Unknown")
    """
    if message in DIRECT_QUESTIONS:
        return "Direct"
    elif message in INDIRECT_QUESTIONS:
        return "Indirect"
    else:
        return "Unknown"
