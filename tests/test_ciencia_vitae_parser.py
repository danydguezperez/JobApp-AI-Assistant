from pathlib import Path
import unittest

from ciencia_vitae_parser import (
    is_ciencia_vitae_text,
    parse_ciencia_vitae,
    parse_languages,
    parse_outputs,
    parse_experience,
)


FIXTURE = """Identification
Personal identification
Full name
Example Researcher
Author identifiers
Ciência ID
ABCD-1234
ORCID iD
0000-0000-0000-0000
Email addresses
example@example.org
Languages
Language Speaking Reading Writing Listening Peer-review
English Advanced (C1)
Portuguese Advanced (C1)
Education
2024/01/01 -
2024/03/01
Concluded
Bioinformatics for Research (Postgraduate Program)
Example University, Portugal
Affiliation
Science
2024/04 - Current Researcher (Research) Example Institute, Portugal
Projects
Grant
Designation Funders
2024/04 - Current Example Omics Project
Researcher
Outputs
Publications
Journal article 1 A. Author; Example Researcher. "A structured publication title". 2024. 10.1234/example.1
Dataset 1 Example Researcher. Example Dataset, Mendeley Data, V1, doi: 10.17632/example.1.
2 Example Researcher. Dataset S2, Mendeley Data, V1, doi: 10.17632/example2.1.
Other output 1 Something else
Activities
Distinctions
2025
Other distinction
Example research award
"""


class CienciaVitaeParserTests(unittest.TestCase):
    def test_detects_and_splits_core_ciencia_vitae_sections(self) -> None:
        self.assertTrue(is_ciencia_vitae_text(FIXTURE))
        profile = parse_ciencia_vitae(FIXTURE)
        self.assertEqual(profile["personal_info"]["full_name"], "Example Researcher")
        self.assertEqual(len(profile["education"]), 1)
        self.assertEqual(len(profile["experience"]), 1)
        self.assertEqual(len(profile["projects"]), 1)
        self.assertEqual(len(profile["publications"]), 1)
        self.assertEqual(len(profile["datasets"]), 2)
        self.assertEqual(len(profile["awards"]), 1)
        self.assertIn("Ciencia Vitae", profile["source_notes"]["mode"].replace("_", " ").title())

    def test_language_levels_are_read_not_assumed(self) -> None:
        text = (
            "Languages\n"
            "Language Speaking Reading Writing Listening Peer-review\n"
            "Spanish Native\n"
            "English Advanced (C1)\n"
            "Italian Intermediate (B1)\n"
            "Education\n2020 - 2024\n"
        )
        levels = {row["language"]: row["level"] for row in parse_languages(text)}
        self.assertEqual(levels["Spanish"], "Native")
        self.assertEqual(levels["English"], "Advanced (C1)")
        self.assertEqual(levels["Italian"], "Intermediate (B1)")
        # A different level must be read verbatim, not overwritten with a default.
        alt = {row["language"]: row["level"]
               for row in parse_languages("Languages\nEnglish Intermediate (B2)\nEducation\nx\n")}
        self.assertEqual(alt["English"], "Intermediate (B2)")

    def test_language_grid_fragments_are_reassembled(self) -> None:
        text = (
            "Languages\n"
            "Language Speaking Reading Writing Listening Peer-review\n"
            "Spanish;\nCastilian\n(Mother tongue)\n"
            "English Advanced\n(C1)\nAdvanced\n(C1)\n"
            "Portuguese Advanced\n(C1)\n"
            "Italian Intermediate\n(B1)\n"
            "Education\n"
        )
        levels = {row["language"]: row["level"] for row in parse_languages(text)}
        self.assertEqual(levels["Spanish; Castilian"], "Native")
        self.assertEqual(levels["English"], "Advanced (C1)")
        self.assertEqual(levels["Portuguese"], "Advanced (C1)")
        self.assertEqual(levels["Italian"], "Intermediate (B1)")

    def test_doi_and_year_are_bound_per_publication(self) -> None:
        text = (
            "Outputs\nPublications\n"
            'Journal article 1 A. Author. "First publication title here". 2021. 10.1111/first.1\n'
            'Journal article 2 B. Author. "Second publication title here". 2023. 10.2222/second.2\n'
            "Activities\n"
        )
        pubs = parse_outputs(text)["publications"]
        self.assertEqual(len(pubs), 2)
        self.assertEqual((pubs[0]["year"], pubs[0]["doi"]), ("2021", "10.1111/first.1"))
        self.assertEqual((pubs[1]["year"], pubs[1]["doi"]), ("2023", "10.2222/second.2"))

    def test_role_is_split_from_institution(self) -> None:
        text = (
            "Affiliation\nScience\n"
            "2024/04 - Current Researcher (Research) Example Institute, Portugal\n"
            "Projects\n"
        )
        experience, _teaching = parse_experience(text)
        self.assertEqual(len(experience), 1)
        self.assertEqual(experience[0]["title"], "Researcher")
        self.assertEqual(experience[0]["company"], "Example Institute, Portugal")
