import tempfile
import unittest
from pathlib import Path

from cv_canonical import canonical_from_ciencia_vitae_xml, render_durable_html, validate_canonical


SAMPLE_XML = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<curriculum>
  <person-info><full-name>Ada Example</full-name></person-info>
  <resume>Computational biologist\nWorks on reproducible science.</resume>
  <email privacy-level=\"publico\"><email-address>ada@example.org</email-address></email>
  <phone-number privacy-level=\"privado\"><local-number>999999999</local-number></phone-number>
  <degree id=\"degree-1\" privacy-level=\"publico\">
    <degree-type>Doctorate</degree-type><degree-name>PhD in Computational Biology</degree-name>
    <institution><institution-name>Example University</institution-name></institution>
    <end-date year=\"2024\" month=\"06\" day=\"01\" />
  </degree>
  <output id=\"output-1\" privacy-level=\"publico\">
    <output-category>Publications</output-category><output-type>Book chapter</output-type>
    <book-chapter><chapter-title>Reproducible Analysis</chapter-title></book-chapter>
    <publication-year>2025</publication-year>
  </output>
</curriculum>"""


class CanonicalCVTests(unittest.TestCase):
    def test_xml_is_structured_and_private_contact_is_not_exported(self) -> None:
        canonical = canonical_from_ciencia_vitae_xml(SAMPLE_XML, "sample.xml")
        self.assertEqual(validate_canonical(canonical), [])
        self.assertEqual(canonical["profile"]["full_name"], "Ada Example")
        self.assertNotIn("phone", canonical["profile"]["contact"])
        self.assertEqual(canonical["sections"]["education"][0]["data"]["title"], "PhD in Computational Biology")
        self.assertEqual(canonical["sections"]["book_chapters"][0]["data"]["title"], "Reproducible Analysis")

        with tempfile.TemporaryDirectory() as temp_dir:
            template = Path(__file__).resolve().parents[1] / "templates" / "durable_cv_template.html"
            output = render_durable_html(canonical, template)
            Path(temp_dir, "cv.html").write_text(output, encoding="utf-8")
        self.assertIn("Ada Example", output)
        self.assertNotIn("999999999", output)
        self.assertNotIn("{{FULL_NAME}}", output)

    def test_skills_are_mapped_from_knowledge_fields_xml(self) -> None:
        xml = b"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<curriculum xmlns:da=\"http://da\" xmlns:common=\"http://common\">
  <person-info><full-name>Dany Test</full-name></person-info>
  <da:domain-activity id=\"dom-1\" privacy-level=\"public\">
    <common:keywords>
      <common:keyword>Biodiscovery</common:keyword>
      <common:keyword>RNA-seq</common:keyword>
      <common:keyword>Proteomics</common:keyword>
    </common:keywords>
  </da:domain-activity>
  <output id=\"out-1\" privacy-level=\"public\">
    <article-title>A paper</article-title>
    <common:keywords><common:keyword>SHOULD-NOT-APPEAR</common:keyword></common:keywords>
  </output>
</curriculum>"""
        canonical = canonical_from_ciencia_vitae_xml(xml, "skills.xml")
        skills = [item["data"]["title"] for item in canonical["sections"]["skills"]]
        self.assertEqual(skills, ["Biodiscovery", "RNA-seq", "Proteomics"])
        self.assertNotIn("SHOULD-NOT-APPEAR", skills)

    def test_consulting_cta_present_only_when_configured(self) -> None:
        canonical = canonical_from_ciencia_vitae_xml(SAMPLE_XML, "sample.xml")
        template = Path(__file__).resolve().parents[1] / "templates" / "durable_cv_template.html"
        plain = render_durable_html(canonical, template)
        self.assertNotIn('<aside class="cv-cta"', plain)
        self.assertNotIn("{{CTA}}", plain)
        with_cta = render_durable_html(
            canonical, template,
            {"cta": {"email": "discover@pagbiomics.com", "url": "https://www.pagbiomics.com"}},
        )
        self.assertIn('<aside class="cv-cta"', with_cta)
        self.assertIn("mailto:discover@pagbiomics.com", with_cta)
        self.assertIn("https://www.pagbiomics.com", with_cta)
        self.assertNotIn("{{CTA}}", with_cta)


if __name__ == "__main__":
    unittest.main()
