from langchain_core.prompts import PromptTemplate

# web search and summarization prompts

# ASSISTANT SELECTION
ASSISTANT_SELECTION_INSTRUCTIONS = """
Sən tədqiqat sualını uyğun tədqiqat köməkçisinə yönləndirmək üzrə mütəxəssissən.
Müxtəlif sahələrdə ixtisaslaşmış bir neçə tədqiqat köməkçisi mövcuddur.
Hər köməkçi xüsusi növ və tədqiqat təlimatları ilə müəyyən edilir.

Uyğun köməkçini seçmək üçün sualın mövzusunu köməkçinin ixtisas sahəsi ilə uyğunlaşdır.

------
Suala əsasən düzgün köməkçi məlumatının necə qaytarılmasına dair nümunələr:

Nümunələr:
Sual: "SOCAR istiqrazlarına sərmayə qoymalıyam?"
Cavab:
{{
    "assistant_type": "Maliyyə analitiki köməkçisi",
    "assistant_instructions": "Sən təcrübəli süni intellekt maliyyə analitiki köməkçisisən. Əsas məqsədin təqdim olunan məlumat və tendensiyalar əsasında əhatəli, obyektiv və sistemli maliyyə hesabatları hazırlamaqdır.",
    "user_question": "{user_question}"
}}
Sual: "Bakıda ən maraqlı görməli yerlər hansılardır?"
Cavab:
{{
    "assistant_type": "Tur bələdçisi köməkçisi",
    "assistant_instructions": "Sən dünya üzrə səyahət təcrübəsi olan süni intellekt tur bələdçisi köməkçisisən. Əsas məqsədin məkanların tarixi, görməli yerləri və mədəni xüsusiyyətləri haqqında maraqlı, obyektiv və yaxşı strukturlaşdırılmış səyahət hesabatları hazırlamaqdır.",
    "user_question": "{user_question}"
}}

Sual: "Hidayət Heydərov uğurlu cüdoçudurmu?"
Cavab:
{{
    "assistant_type": "İdman mütəxəssisi köməkçisi",
    "assistant_instructions": "Sən təcrübəli süni intellekt idman köməkçisisən. Əsas məqsədin idman şəxsləri və hadisələri haqqında faktlar, statistika və təhlillər daxil olmaqla maraqlı, obyektiv və yaxşı strukturlaşdırılmış hesabatlar hazırlamaqdır.",
    "user_question": "{user_question}"
}}

------
Yuxarıdakıları nəzərə alaraq, aşağıdakı sual üçün uyğun tədqiqat köməkçisini seç.
Sual: {user_question}
Cavab:

""" 

ASSISTANT_SELECTION_PROMPT_TEMPLATE = PromptTemplate.from_template( 
    template=ASSISTANT_SELECTION_INSTRUCTIONS
)

# WEB SEARCH
WEB_SEARCH_INSTRUCTIONS = """
{assistant_instructions}

Aşağıdakı sual üzrə mümkün qədər çox məlumat toplamaq üçün {num_search_queries} veb axtarış sorğusu yaz:
{user_question}
Məqsədin tapılan məlumatlar əsasında hesabat hazırlamaqdır. Mənbələrin keyfiyyətini artıracaqsa,
axtarış sorğularını mövzuya uyğun başqa dildə də yaza bilərsən.
Cavabı yalnız aşağıdakı formatda sorğular siyahısı kimi qaytar:
[
    {{"search_query": "sorğu1", "user_question": "{user_question}" }},
    {{"search_query": "sorğu2", "user_question": "{user_question}" }},
    {{"search_query": "sorğu3", "user_question": "{user_question}" }}
]
"""

WEB_SEARCH_PROMPT_TEMPLATE = PromptTemplate.from_template(
    template=WEB_SEARCH_INSTRUCTIONS
)

# INDIVIDUAL SEARCH SUMMARY
SUMMARY_INSTRUCTIONS = """
Aşağıdakı mətni oxu:
Mətn: {search_result_text}

-----------

Aşağıdakı suala yalnız yuxarıdakı mətnə əsaslanaraq Azərbaycan dilində qısa cavab ver.
Sual: {search_query}
 
-----------
Verilmiş mətn əsasında suala cavab vermək mümkün deyilsə, mətni qısa şəkildə xülasə et.
Mövcud olan bütün mühüm faktları, rəqəmləri və statistik məlumatları daxil et.
"""

SUMMARY_PROMPT_TEMPLATE = PromptTemplate.from_template(
    template=SUMMARY_INSTRUCTIONS
)

# RESEARCH REPORT
# Research Report prompts

RESEARCH_REPORT_INSTRUCTIONS = """
Sən tənqidi düşünən süni intellekt tədqiqat köməkçisisən. Məqsədin verilmiş məlumat əsasında yaxşı yazılmış, obyektiv və strukturlaşdırılmış hesabat hazırlamaqdır.

Məlumat:
--------
{research_summary}
--------

Yuxarıdakı məlumatdan istifadə edərək "{user_question}" sualına və ya mövzusuna Azərbaycan dilində ətraflı hesabatla cavab ver. \
Hesabat birbaşa suala yönəlməli, yaxşı strukturlaşdırılmış, informativ və dərin olmalı, \
mümkün olduqda fakt və rəqəmlərə əsaslanmalı və ən azı 1 200 sözdən ibarət olmalıdır.

Təqdim edilmiş bütün uyğun və zəruri məlumatlardan istifadə et.
Hesabatı Markdown sintaksisi ilə yaz.
Verilmiş məlumat əsasında konkret və əsaslandırılmış mövqe formalaşdır. Ümumi və mənasız nəticələrlə kifayətlənmə.
İstifadə olunan bütün mənbə ünvanlarını hesabatın sonunda yaz və təkrar mənbələri yalnız bir dəfə göstər.
Hesabatı APA üslubunda hazırla.
Əlindən gələni et; bu hesabat mənim karyeram üçün çox vacibdir."""

RESEARCH_REPORT_PROMPT_TEMPLATE = PromptTemplate.from_template(
    template=RESEARCH_REPORT_INSTRUCTIONS
)
