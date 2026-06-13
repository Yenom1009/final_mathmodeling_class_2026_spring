import tempfile
import unittest
from pathlib import Path

from src.report_assets import generate_asset_manifest


class ReportAssetManifestChecks(unittest.TestCase):
    def test_generate_asset_manifest_writes_markdown_and_tex(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for dirname in ["figures", "results", "overleaf_report/tables", "docs"]:
                (root / dirname).mkdir(parents=True, exist_ok=True)
            (root / "figures" / "fig01_demo.png").write_bytes(b"png")
            (root / "figures" / "fig01_demo.pdf").write_bytes(b"pdf")
            (root / "results" / "scan_k.csv").write_text("k,y\n0,1\n", encoding="utf-8")

            summary = generate_asset_manifest(root)

            self.assertEqual(summary["figures_png"], 1)
            self.assertEqual(summary["figures_pdf"], 1)
            self.assertEqual(summary["results_csv"], 1)
            md = root / "docs" / "results_asset_manifest.md"
            tex = root / "overleaf_report" / "tables" / "asset_manifest.tex"
            self.assertTrue(md.exists())
            self.assertTrue(tex.exists())
            self.assertIn("fig01_demo.png", md.read_text(encoding="utf-8"))
            self.assertIn("scan\\_k.csv", tex.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
