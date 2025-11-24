import unittest
from unittest.mock import MagicMock, patch
from exporter import GitBookExporter
import os
import shutil

class TestGitBookExporter(unittest.TestCase):
    def setUp(self):
        self.output_dir = "test_output"
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        self.exporter = GitBookExporter("https://example.com", self.output_dir)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch('requests.Session.get')
    def test_run(self, mock_get):
        # Mock response for the main page
        mock_response_main = MagicMock()
        mock_response_main.content = b"""
        <html>
            <nav>
                <a href="/page1">Page 1</a>
            </nav>
            <main>
                <h1>Main Page</h1>
                <p>This is the main page.</p>
            </main>
        </html>
        """
        mock_response_main.raise_for_status.return_value = None

        # Mock response for Page 1
        mock_response_page1 = MagicMock()
        mock_response_page1.content = b"""
        <html>
            <main>
                <h1>Page 1</h1>
                <p>This is page 1.</p>
            </main>
        </html>
        """
        mock_response_page1.raise_for_status.return_value = None

        # Side effect to return different content based on URL
        def side_effect(url):
            if url == "https://example.com":
                return mock_response_main
            elif url == "https://example.com/page1":
                return mock_response_page1
            return MagicMock(content=b"")

        mock_get.side_effect = side_effect

        self.exporter.run()

        # Check if files are created
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "example.com", "html", "index.html")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "example.com", "md", "index.md")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "example.com", "html", "page1.html")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "example.com", "md", "page1.md")))

if __name__ == '__main__':
    unittest.main()
