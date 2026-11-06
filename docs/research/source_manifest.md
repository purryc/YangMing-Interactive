# Wang Yangming Source Manifest

Generated: 2026-06-24

## NotebookLM Upload Set

| Upload file | Role | Source / access note |
| --- | --- | --- |
| `01-primary-chuanxilu-wikisource.md` | Core primary text, readable OCR-free text | Wikisource public-domain text: https://zh.wikisource.org/wiki/傳習錄 |
| `02-biography-mingshi-mingruxuean-wikisource.md` | Biographical and school-history anchor | Wikisource public-domain text: https://zh.wikisource.org/wiki/明史/卷195 and https://zh.wikisource.org/wiki/明儒學案/姚江學案 |
| `01-primary-chuanxilu-wikimedia-scan.pdf` | Scan witness for `传习录` | Wikimedia Commons / Shuge scan, CC BY-SA 4.0 file page: https://zh.wikisource.org/wiki/File:传习录.上下卷.明.王阳明著.明嘉靖二十九年王畿重刻本.黑白版.pdf |
| `01-primary-wang-wencheng-complete-wikimedia.pdf` | Full collected works scan | Wikimedia Commons PDF: https://upload.wikimedia.org/wikipedia/commons/b/b2/NLC416-09jh004222-35822_王文成公全書.pdf |
| `03-philosophy-wang-yangming-henke-1916-internetarchive.pdf` | Public-domain English translation | Internet Archive: https://archive.org/details/philosophyofwang00wangiala |
| `02-biography-historical-background-dong-2020-springer-open.pdf` | Modern open-access life/philosophy narrative | Springer Open / CC BY-NC-ND 4.0: https://link.springer.com/book/10.1007/978-981-15-3036-4 |
| `03-philosophy-zheng-2018-knowledge-action.pdf` | Modern article on 知行合一 | Open web PDF from 学术月刊: https://www.xsyk021.com/fileXSYK/journal/article/xsyk/2018/8/PDF/20180801.pdf |
| `03-philosophy-liangzhi-inner-nccu.txt` | Text extraction of article on 良知 / 心即理 | Original PDF is encrypted with copy restrictions and may fail NotebookLM import, so upload extracted text. Source: https://thinker.nccu.edu.tw/upload/40/publication_file/112/44-1.pdf |
| `03-philosophy-wenlu-to-quanshu-2021.pdf` | Version history from `阳明先生文录` to `王文成公全书` | Open web PDF from 明代研究: https://ming.cnhis.ncnu.edu.tw/wp-content/uploads/2021/07/ming36_03Yang_full.pdf |
| `04-animation-development-brief.md` | Codex-authored adaptation index | Derived guide from the uploaded source set; use it for creative questioning, not as an independent historical authority. |
| `99-manifest-source-map.md` | Source map and caveats | This manifest. |

## Downloaded But Not Primary Upload

| Local file | Reason |
| --- | --- |
| `sources/text/03-philosophy-wang-yangming-henke-1916-ocr.txt` | Duplicate of the Internet Archive PDF OCR; keep as fallback if NotebookLM struggles with the PDF. |
| `sources/text/01-primary-wang-wencheng-complete-wikisource.md` | Wikisource pages were mostly scan indexes, not full text; do not treat as complete. |
| `sources/text/01-primary-wang-wencheng-complete-pdftotext.txt` | Scan PDF has no embedded OCR text. |
| `sources/text/01-primary-chuanxilu-scan-pdftotext.txt` | Scan PDF has no embedded OCR text. |

## Attempted / Blocked

| Source | Status |
| --- | --- |
| Chinese Text Project `王文成公全书` OCR | Useful OCR source found at https://ctext.org/wiki.pl?if=gb&remap=gb&res=483031, but repeated automated requests triggered temporary 403 protection. Retry later with slower/manual access if full machine-readable全集 text is required. |
| OAPEN direct full PDF | OAPEN page is protected by Anubis anti-bot. Springer Open PDF succeeded and contains the full 206-page book. |
| Academia Sinica Kant/Wang PDF | Command-line download returned an HTML error page, removed from pack. |
| PhilArchive / MDPI extras | Command-line PDF requests returned 403, skipped to avoid bad files. |

## NotebookLM Limit Check

Google's NotebookLM Help currently states that each source can contain up to 500,000 words or 200MB for uploaded files, and free notebooks can include up to 50 sources. This upload set stays below that limit.

Official references:

- https://support.google.com/notebooklm/answer/16269187
- https://support.google.com/notebooklm/answer/16215270

## Caveats

- The best-readable primary text in this pack is `传习录`, not the complete全集.
- `王文成公全书` full scan is authoritative as a witness, but OCR is not embedded.
- For exact quotations in a script, verify against the scan or a modern scholarly edition.
- Modern commercial books and translations were intentionally not downloaded unless public-domain or open-access.
