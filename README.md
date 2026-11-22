# MAGNEEFY website

A static, dark editorial website for Magneefy. It's plain HTML, CSS and JS, with no framework and no build step needed to host it.

## Pages
| File | Page |
|---|---|
| `index.html` | Home: hero, business challenges, 4 solutions, approach, process, founder, audience, insights, CTA |
| `what-we-do.html` | Solutions overview + ways to work together |
| `customer-acquisition.html` | Solution 01 |
| `ai-automation.html` | Solution 02 |
| `business-operations.html` | Solution 03 |
| `websites-customer-experience.html` | Solution 04 |
| `about.html` | Story, founder, differences, values |
| `process.html` | 4-step process in detail, engagement models, FAQ |
| `insights.html` | Article list + newsletter signup |
| `contact.html` | Enquiry form |
| `insights/<slug>/index.html` | Six articles, served at `/insights/<slug>/` |

## Editing content
All copy and the shared nav/footer live in `_src/build.py`. Edit it, then regenerate:

```bash
python3 _src/build.py
```

Articles are Markdown files in `_src/articles/` (the settings block at the top holds the title, SEO title, description, category, related articles, linked solution page and call to action). Add `date: 2026-12-01` to an article to include its publish date in the structured data. Featured images are drawn in `_src/articles.py` and written to `assets/img/insights/`.

Styles: `assets/css/style.css` · Behaviour: `assets/js/main.js`.

## Before going live
1. **Founder photo**: save a portrait as `assets/img/jeffery-odiba.jpg` (4:5 ratio). It replaces the "JO" monogram automatically.
2. **Contact email**: set `CONTACT_EMAIL` in `_src/build.py` (currently `hello@magneefy.com`).
3. **Form backend**: the contact form opens the visitor's email app by default. To receive submissions directly, set `data-endpoint` on `#contact-form` (in `build_contact()`) to a Formspree, Basin or similar form endpoint.
4. **Newsletter**: the Insights signup only validates in the browser. Connect it to your email platform (Mailchimp, ConvertKit, etc.).
5. **Social share images**: article featured images are SVG, which Facebook, LinkedIn and X won't show in link previews. Export PNG versions for `og:image` if you want image previews when articles are shared.
6. **Domain**: set `SITE_URL` in `_src/build.py` (used for canonical URLs and `sitemap.xml`), and the LinkedIn URL in the footer.
