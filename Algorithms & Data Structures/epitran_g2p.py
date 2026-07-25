import epitran

epi = epitran.Epitran('aze-Latn')

word = "SOCAR"
exceptions = {
    "SOCAR": "sɔkɑr",
}

ipa_phonemes = exceptions.get(word.upper(), epi.transliterate(word))
#ipa_phonemes = epi.transliterate(word)

print(f"Word: {word}")
print(f"IPA Phonemes: {ipa_phonemes}")

# Output:
# python epitran_g2p.py
# Word: salam! necəsən?
# IPA Phonemes: sɑlɑm! ned͡ʒæsæn?

# Word: SOCAR
# IPA Phonemes: sɔd͡ʒɑr (correct should be: sɔkɑr)

# We can handle exceptions in code:
# exceptions = {
#     "SOCAR": "sɔkɑr",
# }

# ipa_phonemes = exceptions.get(word.upper(), epi.transliterate(word))