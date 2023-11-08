from transformers import pipeline

summarizer = pipeline("summarization")

text = """
In classical physics and general chemistry, matter is any substance that has mass and takes up space by having volume.[1] All everyday objects that can be touched are ultimately composed of atoms, which are made up of interacting subatomic particles, and in everyday as well as scientific usage, matter generally includes atoms and anything made up of them, and any particles (or combination of particles) that act as if they have both rest mass and volume. However it does not include massless particles such as photons, or other energy phenomena or waves such as light or heat.[1]: 21 [2] Matter exists in various states (also known as phases). These include classical everyday phases such as solid, liquid, and gas – for example water exists as ice, liquid water, and gaseous steam – but other states are possible, including plasma, Bose–Einstein condensates, fermionic condensates, and quark–gluon plasma.[3]

Usually atoms can be imagined as a nucleus of protons and neutrons, and a surrounding "cloud" of orbiting electrons which "take up space".[4][5] However this is only somewhat correct, because subatomic particles and their properties are governed by their quantum nature, which means they do not act as everyday objects appear to act – they can act like waves as well as particles, and they do not have well-defined sizes or positions. In the Standard Model of particle physics, matter is not a fundamental concept because the elementary constituents of atoms are quantum entities which do not have an inherent "size" or "volume" in any everyday sense of the word. Due to the exclusion principle and other fundamental interactions, some "point particles" known as fermions (quarks, leptons), and many composites and atoms, are effectively forced to keep a distance from other particles under everyday conditions; this creates the property of matter which appears to us as matter taking up space.
"""

summarizer(text, max_length=130, min_length=30, do_sample=False)
