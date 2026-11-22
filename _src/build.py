#!/usr/bin/env python3
"""MAGNEEFY static site generator.

Shared layout (head, nav, footer, CTA) lives here once; every page is
rendered to plain static HTML in the project root.

    python3 _src/build.py
"""
from pathlib import Path
import html
import json
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import articles as A

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://www.magneefy.com"
CONTACT_EMAIL = "hello@magneefy.com"
YEAR_START = 2026

# ---------------------------------------------------------------- icons
ARROW = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4"/></svg>'
ARROW_BIG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 12h17M14 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.6" aria-hidden="true"><path d="M2.5 8.5l3.5 3.5 7.5-8"/></svg>'
SEARCH = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg>'

IC = {
    "form": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="2.5" y="1.5" width="11" height="13" rx="1.5"/><path d="M5 5h6M5 8h6M5 11h3"/></svg>',
    "crm": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="6" cy="5.5" r="2.5"/><path d="M1.5 14c.6-2.6 2.3-4 4.5-4s3.9 1.4 4.5 4M11 3.5h3.5M11 6.5h3.5"/></svg>',
    "ai": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M8 1.5l1.6 4.2L14 7.3l-4.4 1.6L8 13.2 6.4 8.9 2 7.3l4.4-1.6z"/></svg>',
    "mail": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="1.5" y="3" width="13" height="10" rx="1.5"/><path d="M2 4l6 5 6-5"/></svg>',
    "cal": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="1.5" y="2.5" width="13" height="12" rx="1.5"/><path d="M1.5 6.5h13M5 1v3M11 1v3"/></svg>',
    "hook": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 11a3 3 0 1 1 1.5-5.6L9 9.5M11 5a3 3 0 1 1-1.5 5.6M8 3l-2.5 4.5h5"/></svg>',
    "slack": '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M2 4.5h12v7H8l-3 2.5v-2.5H2z"/></svg>',
}

MARK = '''<svg class="mark" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 21V5.5a2.5 2.5 0 0 1 5 0V21" fill="none" stroke="#FFFFFF" stroke-width="2.6"/><path d="M16 21V5.5a2.5 2.5 0 0 1 5 0V21" fill="none" stroke="#FFFFFF" stroke-width="2.6"/><path d="M8 7.5 12 14l4-6.5" fill="none" stroke="#26C982" stroke-width="2.6" stroke-linejoin="round"/><circle cx="12" cy="20" r="1.9" fill="#26C982"/></svg>'''

WORDMARK = f'<a href="index.html" class="wordmark" aria-label="Magneefy home">{MARK}<span>MAGN<b>EE</b>FY</span></a>'

NAV = [
    ("index.html", "Home", "home"),
    ("what-we-do.html", "What We Do", "services"),
    ("about.html", "About", "about"),
    ("process.html", "Our Process", "process"),
    ("insights.html", "Insights", "insights"),
    ("contact.html", "Contact", "contact"),
]


def e(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- solutions data
SOLUTIONS = [
    {
        "slug": "customer-acquisition",
        "num": "01",
        "name": "Customer Acquisition & Digital Marketing",
        "short": "Customer Acquisition",
        "headline": "Get Found by the Right People. Turn Attention Into Business.",
        "headline_html": 'Get Found by the Right People. <span class="hl">Turn Attention Into Business.</span>',
        "desc": "Build a stronger digital presence, attract relevant audiences, and create marketing campaigns designed to generate qualified enquiries and business opportunities.",
        "intro": "Most businesses don’t have a visibility problem or an advertising problem. They have a clarity problem: activity across many channels, with no clear line between what was spent and who became a customer. We start with that line and build outward.",
        "services": [
            ("Digital marketing strategy", "A practical plan that ties channels, budget and messaging to the customers you actually want."),
            ("Social media management", "Consistent, on-brand publishing and community management that keeps you visible between sales."),
            ("Paid advertising", "Campaign planning, creative direction and budget control across paid channels."),
            ("Meta Ads management", "Facebook and Instagram campaigns built around clear audiences, offers and lead quality."),
            ("Google Ads management", "Search and Performance Max campaigns that reach people already looking for what you sell."),
            ("Search engine optimization", "Technical fixes, content and on-page work that help you rank for the searches that matter."),
            ("Local SEO", "Google Business Profile, citations and reviews set up to win nearby, high-intent customers."),
            ("AI Search Optimization", "Making sure AI assistants can find, understand and accurately describe your business."),
            ("Answer Engine Optimization (AEO)", "Structuring content so it becomes the direct answer to your customers’ questions."),
            ("Generative Engine Optimization (GEO)", "Building the authority signals that get you cited in AI-generated recommendations."),
            ("Content marketing", "Articles, guides and posts that answer real buyer questions and build trust before the first call."),
            ("Marketing performance tracking", "Analytics, conversion tracking and simple reporting that show what is producing customers."),
        ],
        "outcomes": ["Improved online visibility", "More qualified enquiries", "Better marketing consistency", "Stronger conversion opportunities", "Clearer campaign performance"],
        "fit_for": [
            "You’re spending on marketing but can’t say which channel produces customers",
            "Enquiries are inconsistent from month to month",
            "Competitors show up in search and AI answers where you don’t",
            "Your social presence is irregular or doesn’t reflect the quality of your work",
        ],
        "deliver": [
            "A channel plan prioritised by likely return, not by trend",
            "Campaigns built, launched and managed against agreed goals",
            "Conversion tracking that connects activity to enquiries",
            "Plain-English reporting with clear next actions",
        ],
        "faq": [
            ("How soon will we see results?", "Paid campaigns can produce enquiries within weeks of launch once tracking and targeting are right. SEO, local SEO and AI search visibility compound over months. We’ll set realistic expectations for each channel before any work begins."),
            ("What is AI search optimization, and do we need it?", "More buyers now ask AI assistants for recommendations instead of scrolling search results. AEO and GEO make sure those tools can find accurate, well-structured information about your business and are more likely to mention you. If your customers research before buying, it’s worth addressing now."),
            ("Do you manage ad budgets directly?", "Ad spend is paid directly to platforms like Meta and Google from your own accounts, so you always retain ownership and visibility. We manage the campaigns inside them."),
            ("Can you work alongside our in-house team?", "Yes. We can own a channel end-to-end, or support an existing marketer with strategy, execution capacity and tracking."),
        ],
    },
    {
        "slug": "ai-automation",
        "num": "02",
        "name": "AI Automation & Business Systems",
        "short": "AI Automation",
        "headline": "Stop Repeating Tasks That Technology Can Handle.",
        "headline_html": 'Stop Repeating Tasks <span class="hl">That Technology Can Handle.</span>',
        "desc": "Connect business tools, automate repetitive workflows, and create smarter systems that help teams operate more efficiently.",
        "intro": "Every growing business accumulates manual work: copying details between tools, chasing replies, sending the same emails, updating the same spreadsheets. We map where those hours go, then connect your systems so the routine work happens on its own, reliably.",
        "services": [
            ("Make.com automation", "Multi-step scenarios that move data between your apps with logic, filters and error handling."),
            ("Zapier integrations", "Fast, dependable connections between the tools your team already uses."),
            ("AI workflow automation", "Workflows that use AI to read, sort, summarise and draft, with human checks where they matter."),
            ("AI assistants and agents", "Custom assistants trained on your processes to answer questions and complete defined tasks."),
            ("CRM automation", "Pipelines that update themselves: stages, owners, reminders and records kept current."),
            ("Automated lead capture", "Every form, ad lead and enquiry captured, enriched and routed to the right place instantly."),
            ("Automated follow-ups", "Timely, personal follow-up sequences so no enquiry goes cold through silence."),
            ("Appointment booking automation", "Self-serve booking with confirmations, reminders and rescheduling handled automatically."),
            ("API integrations", "Custom connections for tools that don’t integrate out of the box."),
            ("Webhooks", "Real-time triggers that let your systems react the moment something happens."),
            ("Customer support automation", "Instant answers to common questions and clean hand-offs to a person when needed."),
            ("Business process automation", "End-to-end automation of onboarding, invoicing, reporting and other recurring processes."),
        ],
        "outcomes": ["Less repetitive work", "Faster lead response", "More organized customer information", "Reduced manual administration", "Better workflow consistency"],
        "fit_for": [
            "Your team re-types the same information into several tools",
            "New leads wait hours or days for a first response",
            "Processes work only when a specific person remembers to do them",
            "You’ve bought software that was never properly connected",
        ],
        "deliver": [
            "A workflow audit showing where time is lost and what to automate first",
            "Documented, tested automations built on Make.com, Zapier or custom code",
            "Error alerts and monitoring so failures don’t go unnoticed",
            "Handover notes and training so your team understands every system",
        ],
        "faq": [
            ("Make.com or Zapier: which is better?", "It depends on the complexity, volume and budget. Zapier is quick to set up and great for simpler connections; Make.com handles complex, multi-branch logic more cost-effectively. We recommend based on your workflows, not preference."),
            ("Will automation replace our team?", "The aim is to remove repetitive work, not people. Automation gives your team back time for the judgement, relationships and problem-solving that actually grow the business."),
            ("Is AI safe to use with customer data?", "We design workflows with data access kept to what’s necessary, use reputable platforms, and keep a human review step wherever accuracy or sensitivity matters."),
            ("What happens if an automation breaks?", "Every build includes error handling and notifications. Ongoing support plans cover monitoring, fixes and updates as your tools change."),
        ],
    },
    {
        "slug": "business-operations",
        "num": "03",
        "name": "Virtual Assistance & Business Operations",
        "short": "Business Operations",
        "headline": "Get the Support Your Business Needs to Run Smoothly.",
        "headline_html": 'Get the Support Your Business <span class="hl">Needs to Run Smoothly.</span>',
        "desc": "Reliable operational and administrative support for businesses that need structure, organization, and consistent execution.",
        "intro": "When everything routes through the owner, growth stalls. We take on the coordination, administration and day-to-day operational work, and we build the structure (documented processes, organised workspaces, clear ownership) that keeps things running without constant supervision.",
        "services": [
            ("Executive virtual assistance", "Proactive, high-trust support for founders and leaders who need their time protected."),
            ("Administrative support", "The everyday admin, data entry and paperwork handled accurately and on time."),
            ("Inbox management", "Inboxes triaged, organised and answered so important messages surface fast."),
            ("Calendar management", "Diaries kept clean, meetings scheduled across time zones, and focus time protected."),
            ("Customer support", "Courteous, consistent responses to customer enquiries across email and chat."),
            ("Appointment scheduling", "Bookings coordinated, confirmed and followed up without back-and-forth."),
            ("Project coordination", "Timelines, tasks and stakeholders tracked so projects land on schedule."),
            ("Team coordination", "Stand-ups, updates and handovers organised so everyone knows what’s next."),
            ("Notion workspace management", "A single, structured workspace for projects, docs, wikis and team knowledge."),
            ("SOP documentation", "Clear, usable standard operating procedures written from how the work really happens."),
            ("Business process management", "Processes mapped, simplified and owned, so quality doesn’t depend on memory."),
            ("Research and data management", "Market, supplier and prospect research, with data kept clean and usable."),
        ],
        "outcomes": ["Better organized operations", "More time for strategic work", "Consistent administrative support", "Improved task accountability", "More efficient team coordination"],
        "fit_for": [
            "You spend more time coordinating than leading",
            "Important emails and follow-ups slip through the cracks",
            "Knowledge lives in people’s heads instead of documented processes",
            "You need dependable support without hiring a full in-house team",
        ],
        "deliver": [
            "Dedicated support working across US and UK business hours",
            "Agreed response times, priorities and communication channels",
            "Documented SOPs and an organised workspace you own",
            "Regular check-ins and clear visibility of what’s been done",
        ],
        "faq": [
            ("How is this different from hiring a freelance assistant?", "You get operational thinking, not just task completion. Alongside daily support, we document processes, organise your systems and connect them with automation where it saves time."),
            ("Which tools do you work with?", "Google Workspace, Microsoft 365, Notion, Slack, Asana, Trello, ClickUp, HubSpot and most common CRMs and booking tools. If you use something else, we’ll learn it."),
            ("How do you handle confidential information?", "Access is granted through your own accounts with the minimum permissions needed, and we’re happy to work under an NDA."),
            ("Can support scale up or down?", "Yes. Support is arranged around agreed hours or responsibilities and can be adjusted as your needs change."),
        ],
    },
    {
        "slug": "websites-customer-experience",
        "num": "04",
        "name": "Websites, Content & Customer Experience",
        "short": "Websites & Experience",
        "headline": "Make Every Customer Interaction Count.",
        "headline_html": 'Make Every Customer <span class="hl">Interaction Count.</span>',
        "desc": "Create professional digital experiences that build trust, communicate value, and make it easier for customers to take action.",
        "intro": "Your website, emails and content are often a customer’s first and most frequent experience of your business. We design each touchpoint to do a specific job: earn trust, explain value clearly, and make the next step obvious, then connect them into one consistent journey.",
        "services": [
            ("WordPress website development", "Fast, secure WordPress sites your team can update without a developer."),
            ("Business website design", "Clear, credible websites structured around what your customers need to know."),
            ("Landing page development", "Focused pages for campaigns and offers, built to turn visits into enquiries."),
            ("E-commerce websites", "Online stores with smooth product discovery, checkout and order communication."),
            ("Website maintenance", "Updates, backups, security and performance monitoring handled for you."),
            ("Conversion optimization", "Testing and refining pages, forms and calls to action based on real behaviour."),
            ("Social media content creation", "Graphics, carousels and copy designed for your brand and each platform."),
            ("Short-form video content", "Reels, Shorts and TikToks edited to hold attention and communicate quickly."),
            ("Email marketing", "Newsletters and campaigns that keep customers engaged and bring them back."),
            ("Email automation", "Welcome, nurture and re-engagement sequences that run in the background."),
            ("Customer journey optimization", "Every step from first visit to repeat purchase mapped and improved."),
            ("CRM setup and management", "A CRM configured around your sales process, with clean data and clear stages."),
        ],
        "outcomes": ["Stronger online credibility", "Better customer experiences", "More effective landing pages", "Consistent brand communication", "Improved customer follow-up"],
        "fit_for": [
            "Your website no longer reflects the quality of your business",
            "Visitors arrive but rarely enquire or buy",
            "Customers hear from you inconsistently after they first get in touch",
            "Content creation keeps slipping down the priority list",
        ],
        "deliver": [
            "Websites and landing pages structured around a clear next step",
            "Content and email produced to a consistent brand standard",
            "CRM and email systems connected to your website",
            "Ongoing maintenance and optimisation once you’re live",
        ],
        "faq": [
            ("Do you only build on WordPress?", "WordPress is our default for business sites because it’s flexible and easy to own. For stores we also work with WooCommerce and Shopify, and we’ll recommend whatever fits your goals best."),
            ("Will we be able to update the site ourselves?", "Yes. Sites are built so your team can edit pages, posts and products, and we provide a walkthrough at handover."),
            ("Can you write the content as well?", "Yes. We can write website copy, emails and social content, working from your expertise and voice so it sounds like you."),
            ("What happens after launch?", "We offer maintenance and optimisation support covering updates, security, backups and ongoing conversion improvements."),
        ],
    },
]


# ---------------------------------------------------------------- visuals
def visual_acquisition():
    return f'''<div class="vframe" aria-hidden="true">
  <div class="v-search">
    <div class="searchbar">{SEARCH}<span>best accounting firm for small businesses near me</span><span class="caret"></span></div>
    <div class="ui ai-answer">
      <div class="label">{IC["ai"].replace('<svg', '<svg width="12" height="12"')} AI Overview</div>
      <p>For small businesses, look for a firm offering monthly bookkeeping, tax planning and fast responses. <mark>Your Business</mark> is frequently recommended for clear fixed-fee packages and same-week onboarding.</p>
      <div class="cite"><span class="me">yourbusiness.com</span><span>google.com/maps</span><span>industry directory</span></div>
    </div>
    <div class="ui">
      <div class="ui-bar"><span class="t"><i></i>Campaigns</span><span class="tag">Tracking on</span></div>
      <table class="camp">
        <thead><tr><th>Channel</th><th>Status</th><th>Lead quality</th><th></th></tr></thead>
        <tbody>
          <tr><td>Google Search</td><td><span class="dot"></span>Active</td><td>High intent</td><td><svg class="spark" viewBox="0 0 64 18"><polyline points="0,15 10,13 20,14 30,9 40,10 50,5 64,3" fill="none" stroke="#26C982" stroke-width="1.6"/></svg></td></tr>
          <tr><td>Meta Lead Ads</td><td><span class="dot"></span>Active</td><td>Qualifying</td><td><svg class="spark" viewBox="0 0 64 18"><polyline points="0,12 10,14 20,10 30,11 40,7 50,8 64,6" fill="none" stroke="#26C982" stroke-width="1.6"/></svg></td></tr>
          <tr><td>Local SEO</td><td><span class="dot"></span>Growing</td><td>High intent</td><td><svg class="spark" viewBox="0 0 64 18"><polyline points="0,16 10,15 20,13 30,12 40,9 50,7 64,4" fill="none" stroke="#26C982" stroke-width="1.6"/></svg></td></tr>
          <tr><td>Display retargeting</td><td><span class="dot off"></span>Paused</td><td>Under review</td><td><svg class="spark" viewBox="0 0 64 18"><polyline points="0,8 10,9 20,11 30,10 40,12 50,12 64,13" fill="none" stroke="#5E6862" stroke-width="1.6"/></svg></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>'''


def visual_automation():
    n = lambda cls, left, top, ic, small, title: f'<div class="anode {cls}" style="left:{left};top:{top}"><div class="ic">{IC[ic]}</div><small>{small}</small><b>{title}</b></div>'
    return f'''<div class="vframe" aria-hidden="true">
  <div class="v-auto">
    <svg class="wires" viewBox="0 0 100 100" preserveAspectRatio="none">
      <path class="wire live" d="M32 19 C 36 19, 34 47, 38 47"/>
      <path class="wire live" d="M70 47 C 83 47, 83 56, 83 66"/>
      <path class="wire" d="M54 60 C 54 66, 18 62, 18 69"/>
      <path class="wire live" d="M34 81 C 46 81, 54 79, 66 79"/>
    </svg>
    {n("trig", "0", "6%", "form", "Trigger", "New website enquiry")}
    {n("ai", "38%", "34%", "ai", "AI step", "Qualify &amp; summarise lead")}
    {n("", "2%", "69%", "crm", "CRM", "Create deal, assign owner")}
    {n("", "66%", "66%", "mail", "Email", "Personal follow-up sent")}
    <div class="ui run-log">
      <div><span>run #2418</span><span>success</span></div>
      <div><span>run #2417</span><span>success</span></div>
      <div><span>run #2416</span><span>success</span></div>
    </div>
  </div>
</div>'''


def visual_operations():
    return f'''<div class="vframe" aria-hidden="true">
  <div class="v-ops">
    <div class="ui cal">
      <div class="ui-bar"><span class="t"><i></i>This week</span><span class="tag dim">Calendar</span></div>
      <div class="cal-grid">
        <div class="h t"></div><div class="h">Mon</div><div class="h">Tue</div><div class="h">Wed</div>
        <div class="t">9:00</div><div><span class="ev tall">Focus: strategy (protected)</span></div><div><span class="ev dim">Team stand-up</span></div><div><span class="ev">Client onboarding</span></div>
        <div class="t">10:00</div><div></div><div><span class="ev">Sales call — prepped</span></div><div></div>
        <div class="t">11:00</div><div><span class="ev dim">Inbox review</span></div><div></div><div><span class="ev tall">Partner meeting (agenda sent)</span></div>
        <div class="t">12:00</div><div></div><div><span class="ev dim">Supplier follow-up</span></div><div></div>
      </div>
    </div>
    <div style="display:grid;gap:12px">
      <div class="ui">
        <div class="ui-bar"><span class="t"><i></i>Today</span><span class="tag">5 / 7</span></div>
        <div class="ui-body" style="padding:6px 14px">
          <ul class="tasks">
            <li class="done"><span class="cb">{CHECK}</span><span>Inbox triaged &amp; flagged</span></li>
            <li class="done"><span class="cb">{CHECK}</span><span>Onboarding SOP updated</span></li>
            <li class="done"><span class="cb">{CHECK}</span><span>Invoices sent to 4 clients</span></li>
            <li><span class="cb"></span><span>Prep board-meeting notes<small>Due 3:00 PM</small></span></li>
          </ul>
        </div>
      </div>
      <div class="ui">
        <div class="ui-body" style="padding:6px 14px">
          <div class="inbox-row"><b>Needs your reply</b><span class="tag">2</span></div>
          <div class="inbox-row"><span>Handled for you</span><span class="tag dim">18</span></div>
        </div>
      </div>
    </div>
  </div>
</div>'''


def visual_experience():
    return f'''<div class="vframe" aria-hidden="true" style="padding-bottom:56px">
  <div class="v-web">
    <div class="ui browser">
      <div class="ui-bar"><span class="ui-dots"><span></span><span></span><span></span></span><span class="url">yourbusiness.com/book-a-consultation</span></div>
      <div class="lp">
        <div>
          <span class="k">TRUSTED LOCAL EXPERTS</span>
          <h5>The clear next step for your customers.</h5>
          <div class="ln" style="width:92%"></div><div class="ln" style="width:76%"></div><div class="ln" style="width:60%"></div>
          <span class="cta">Book a free consultation →</span>
        </div>
        <div class="img"></div>
      </div>
      <div class="lp-foot"><div><i></i><i></i></div><div><i></i><i></i></div><div><i></i><i></i></div></div>
    </div>
    <div class="ui journey">
      <div class="ui-bar"><span class="t"><i></i>Customer journey</span></div>
      <div class="ui-body" style="padding:6px 14px">
        <div class="step"><i>1</i>Visits landing page<em>Day 0</em></div>
        <div class="step"><i>2</i>Books consultation<em>Day 0</em></div>
        <div class="step"><i>3</i>Welcome email + prep guide<em>Day 0</em></div>
        <div class="step"><i>4</i>Reminder &amp; follow-up<em>Day 2</em></div>
      </div>
    </div>
  </div>
</div>'''


VISUALS = {
    "customer-acquisition": visual_acquisition,
    "ai-automation": visual_automation,
    "business-operations": visual_operations,
    "websites-customer-experience": visual_experience,
}


def hero_ecosystem():
    return f'''<div class="eco eco-in" role="img" aria-label="Illustration of a connected business system: a lead dashboard, CRM pipeline, automated workflow and customer messaging working together.">
  <span class="eco-label" style="left:2px;top:4px">Lead generation</span>
  <div class="ui ui-dash">
    <div class="ui-bar"><span class="t"><i></i>Enquiries overview</span><span class="ui-dots"><span></span><span></span><span></span></span></div>
    <div class="ui-body">
      <div class="dash-top">
        <div><div class="label">Qualified enquiries</div><div class="kpi">Trending up</div></div>
        <span class="tag">Last 90 days</span>
      </div>
      <div class="dash-chart">
        <svg viewBox="0 0 300 120" preserveAspectRatio="none">
          <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#26C982" stop-opacity=".35"/><stop offset="1" stop-color="#26C982" stop-opacity="0"/></linearGradient></defs>
          <g stroke="#29332D" stroke-width="1"><line x1="0" y1="30" x2="300" y2="30"/><line x1="0" y1="60" x2="300" y2="60"/><line x1="0" y1="90" x2="300" y2="90"/></g>
          <polyline points="0,96 30,92 60,94 90,86 120,88 150,80 180,82 210,76 240,78 270,72 300,74" fill="none" stroke="#A5ADA7" stroke-opacity=".4" stroke-width="1.5" stroke-dasharray="3 4"/>
          <path d="M0,98 L30,90 L60,92 L90,78 L120,80 L150,62 L180,64 L210,48 L240,44 L270,30 L300,22 L300,120 L0,120 Z" fill="url(#g1)"/>
          <polyline points="0,98 30,90 60,92 90,78 120,80 150,62 180,64 210,48 240,44 270,30 300,22" fill="none" stroke="#26C982" stroke-width="2.2"/>
          <circle cx="300" cy="22" r="4" fill="#26C982"/>
        </svg>
      </div>
      <div class="dash-legend"><span>With connected follow-up</span><span class="b">Before</span></div>
      <div class="dash-sources">
        <div>Search<b>Organic</b></div><div>Paid<b>Google</b></div><div>Social<b>Meta</b></div><div>AI<b>Answers</b></div>
      </div>
    </div>
  </div>

  <div class="ui ui-crm">
    <div class="ui-bar"><span class="t"><i></i>CRM pipeline</span><span class="tag dim">Live</span></div>
    <div class="ui-body">
      <div class="pipe">
        <div class="pipe-col"><div class="label"><span>New</span><span>4</span></div>
          <div class="deal hot"><b>Harper &amp; Co.</b><small>Web · 2m ago</small><div class="bar"><i style="width:30%"></i></div></div>
          <div class="deal"><b>Northlane Realty</b><small>Meta lead</small><div class="bar"><i style="width:20%"></i></div></div>
        </div>
        <div class="pipe-col"><div class="label"><span>Contacted</span><span>3</span></div>
          <div class="deal"><b>Aldridge Dental</b><small>Call booked</small><div class="bar"><i style="width:55%"></i></div></div>
          <div class="deal"><b>Ostra Studio</b><small>Follow-up 2</small><div class="bar"><i style="width:48%"></i></div></div>
        </div>
        <div class="pipe-col"><div class="label"><span>Proposal</span><span>2</span></div>
          <div class="deal"><b>Kestrel Coaching</b><small>Sent Tue</small><div class="bar"><i style="width:80%"></i></div></div>
        </div>
      </div>
    </div>
  </div>

  <div class="ui ui-flow">
    <div class="ui-bar"><span class="t"><i></i>Automation · New lead</span><span class="tag">Running</span></div>
    <div class="ui-body">
      <div class="flow">
        <div class="node"><span class="ic">{IC["form"]}</span><div><b>Form submitted</b><small>Website · Contact page</small></div><span class="ok">{CHECK}</span></div>
        <div class="link"></div>
        <div class="node"><span class="ic">{IC["ai"]}</span><div><b>AI qualifies &amp; tags lead</b><small>Service · budget · urgency</small></div><span class="ok">{CHECK}</span></div>
        <div class="link"></div>
        <div class="node"><span class="ic">{IC["crm"]}</span><div><b>Deal created in CRM</b><small>Owner assigned</small></div><span class="ok">{CHECK}</span></div>
      </div>
    </div>
  </div>

  <div class="ui ui-chat">
    <div class="ui-bar"><span class="t"><i></i>Inbox</span><span class="tag dim">Auto-reply</span></div>
    <div class="ui-body">
      <div class="msg in">Hi, do you have availability for a consultation next week?<span class="meta">Sarah · 10:42</span></div>
      <div class="msg out">Thanks Sarah! Here are a few times that work. Pick one and it’s booked:
        <div class="slots"><span>Tue 10:00</span><span>Wed 14:30</span><span>Thu 09:00</span></div>
        <span class="meta">Sent instantly</span></div>
      <div class="typing"><i></i><i></i><i></i></div>
    </div>
  </div>
  <span class="eco-label" style="right:2px;bottom:-26px">Customer communication</span>
</div>'''


# ---------------------------------------------------------------- layout
def head(title, desc, path, extra=""):
    url_path = re.sub(r"(^|/)index\.html$", r"\1", path)
    canonical = SITE_URL + "/" + url_path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#0B0D0C">
<meta property="og:type" content="{"article" if path.startswith("insights/") else "website"}">
<meta property="og:site_name" content="Magneefy">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
{extra}
</head>'''


def nav(active):
    links = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if key == active else ""}>{label}</a></li>'
        for href, label, key in NAV
    )
    mlinks = "".join(
        f'<li><a href="{href}">{label}<small>0{i + 1}</small></a></li>' for i, (href, label, _) in enumerate(NAV)
    )
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    {WORDMARK}
    <nav aria-label="Primary"><ul class="nav-links">{links}</ul></nav>
    <div class="nav-cta">
      <a href="contact.html" class="btn btn-primary">Let’s Talk {ARROW}</a>
      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <nav aria-label="Mobile"><ul>{mlinks}</ul></nav>
  <a href="contact.html" class="btn btn-primary btn-lg">Let’s Talk About Your Business {ARROW}</a>
</div>'''


def cta_block(title_html=None, text=None):
    title_html = title_html or 'Ready to grow smarter and <span class="hl">operate better?</span>'
    text = text or "Tell us where your business is today and where you want it to be. We’ll come back with practical recommendations, whether or not we end up working together."
    return f'''<section class="cta-block">
  <div class="wrap">
    <span class="eyebrow reveal">Let’s talk</span>
    <h2 class="reveal d1" style="margin-top:28px">{title_html}</h2>
    <div class="cta-row reveal d2">
      <p>{text}</p>
      <a href="contact.html" class="btn btn-primary btn-lg">Let’s Talk About Your Business {ARROW}</a>
    </div>
  </div>
</section>'''


def footer():
    sol_links = "".join(f'<li><a href="{s["slug"]}.html">{s["short"]}</a></li>' for s in SOLUTIONS)
    return f'''<footer class="footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        {WORDMARK}
        <p class="tagline">More Customers. Better Systems. <span class="hl">Less Busywork.</span></p>
        <p class="muted" style="max-width:26em;font-size:15px">Digital growth, automation and business operations support for growing businesses in the US and UK.</p>
      </div>
      <div><h4>Solutions</h4><ul>{sol_links}</ul></div>
      <div><h4>Company</h4><ul>
        <li><a href="about.html">About</a></li><li><a href="process.html">Our Process</a></li><li><a href="insights.html">Insights</a></li><li><a href="contact.html">Contact</a></li>
      </ul></div>
      <div><h4>Get in touch</h4><ul>
        <li><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></li>
        <li><a href="contact.html">Start a project</a></li>
        <li><a href="https://www.linkedin.com/" rel="noopener">LinkedIn</a></li>
      </ul></div>
    </div>
    <div class="footer-giant" aria-hidden="true">MAGNEEFY</div>
    <div class="footer-bottom">
      <span>© <span data-year>{YEAR_START}</span> Magneefy. Founded by Jeffery Odiba.</span>
      <span>Grow Smarter. Operate Better.</span>
    </div>
  </div>
</footer>
<script src="assets/js/main.js" defer></script>'''


def page(path, title, desc, active, body, extra_head=""):
    out = f'''{head(title, desc, path, extra_head)}
<body>
{nav(active)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    depth = path.count("/")
    if depth:
        prefix = "../" * depth
        out = re.sub(r'(href|src)="(?!https?:|mailto:|tel:|#|/|data:)', lambda m: f'{m.group(1)}="{prefix}', out)
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")
    print("wrote", path)


# ---------------------------------------------------------------- shared sections
CHALLENGES = [
    ("Too Many Enquiries, Not Enough Conversions.", "Potential customers show interest, but inconsistent follow-ups and poor lead management cost businesses opportunities."),
    ("Marketing That Doesn’t Deliver Enough.", "Businesses invest in content, advertising, and SEO without always understanding which activities generate actual customers."),
    ("Too Much Manual Work.", "Repetitive administrative tasks consume valuable hours that could be spent on business growth."),
    ("Disconnected Business Systems.", "Customer information, appointments, projects, and communication sit across different tools without a clear process."),
    ("Operations That Depend on the Owner.", "Business owners spend too much time coordinating everyday activities instead of focusing on strategic decisions."),
    ("Inconsistent Customer Communication.", "Slow responses, missed enquiries, and poor follow-ups create unnecessary friction in the customer journey."),
]

PROCESS = [
    ("Discover", "We start with your business, not our services: your goals, customers, team, tools, and where time and opportunities are currently being lost."),
    ("Diagnose & Plan", "We identify the bottlenecks that matter most and turn them into a prioritised, practical roadmap with clear outcomes and scope."),
    ("Build & Implement", "We set up campaigns, automations, systems and support, testing everything properly and documenting how it works."),
    ("Run, Measure & Improve", "We manage, monitor and report in plain English, then keep refining what works and fixing what doesn’t."),
]


def process_section(head_html=True):
    steps = "".join(
        f'<div class="step-card"><div class="bar"></div><span class="n">{i + 1:02d}<sup>STEP</sup></span><h3>{t}</h3><p>{d}</p></div>'
        for i, (t, d) in enumerate(PROCESS)
    )
    return f'<div class="process">{steps}</div>'


def solution_block(s, i):
    chips = "".join(f"<li>{e(n)}</li>" for n, _ in s["services"][:7])
    more = len(s["services"]) - 7
    chips += f'<li class="more">+{more} more</li>'
    outs = "".join(f"<li>{o}</li>" for o in s["outcomes"][:4])
    flip = " flip" if i % 2 else ""
    return f'''<article class="sol{flip}" id="{s["slug"]}">
  <div class="sol-copy reveal">
    <div class="sol-top"><span class="outline-num">{s["num"]}</span><span class="eyebrow">Solution {s["num"]}<span class="muted" style="letter-spacing:.12em">{s["name"]}</span></span></div>
    <h3>{s["headline_html"]}</h3>
    <p>{s["desc"]}</p>
    <ul class="chips" aria-label="Services included">{chips}</ul>
    <ul class="outcomes-mini" aria-label="Business outcomes">{outs}</ul>
    <a href="{s["slug"]}.html" class="link-arrow">Explore {s["short"]} {ARROW}</a>
  </div>
  <div class="sol-visual reveal d2">{VISUALS[s["slug"]]()}</div>
</article>'''


def founder_section(full=False):
    extra = ""
    if full:
        extra = '''<p class="muted">Jeffery’s background spans executive virtual assistance, business operations management and hands-on digital delivery: running inboxes and calendars, documenting processes, building automations, managing campaigns and launching websites. That combination is the foundation of Magneefy’s approach: growth only lasts when the operations behind it can keep up.</p>'''
    return f'''<div class="founder">
  <div class="portrait reveal">
    <div class="portrait-frame">
      <img src="assets/img/jeffery-odiba.jpg" alt="Jeffery Odiba, founder of Magneefy" loading="lazy">
      <div class="mono">JO<small>FOUNDER PORTRAIT</small></div>
    </div>
    <div class="portrait-tag"><b>Jeffery Odiba</b>Founder, Magneefy</div>
  </div>
  <div class="reveal d1">
    <span class="eyebrow">The founder</span>
    <h2 class="h2">Built by someone who has <span class="hl">run the operations</span>, not just advised on them.</h2>
    <ul class="roles"><li>Virtual Assistant</li><li>Business Operations Manager</li><li>Digital Solutions Specialist</li></ul>
    <div class="belief"><small>THE MAGNEEFY BELIEF</small><p>Most business owners don’t need more tools or more advice. They need a partner who understands how the pieces connect, and who will do the work to make them run.</p></div>
    <p class="muted">Jeffery Odiba founded Magneefy to give growing businesses one dependable partner across marketing, automation and day-to-day operations, so owners can stop holding everything together themselves and focus on the decisions that move the business forward.</p>
    {extra}
    <a href="about.html" class="link-arrow" style="margin-top:10px">More about Magneefy {ARROW}</a>
  </div>
</div>'''


AUDIENCE = ["Consulting firms", "Coaches & consultants", "Real estate", "E-commerce", "Professional services", "Growing startups", "Local service businesses", "Founder-led SMEs"]


def audience_strip():
    return '<div class="audience reveal">' + "".join(f"<div>{a}<span>{i + 1:02d}</span></div>" for i, a in enumerate(AUDIENCE)) + "</div>"


ARTICLES = A.load_articles()
ART_BY_SLUG = {a["slug"]: a for a in ARTICLES}


def post_art(kind):
    if kind == 0:
        return '<svg viewBox="0 0 400 150" preserveAspectRatio="xMidYMid meet"><g fill="none" stroke="#29332D"><circle cx="200" cy="75" r="30"/><circle cx="200" cy="75" r="60"/><circle cx="200" cy="75" r="95"/><circle cx="200" cy="75" r="135"/></g><circle cx="200" cy="75" r="10" fill="#26C982"/><g fill="#16A36A"><circle cx="258" cy="60" r="4"/><circle cx="130" cy="100" r="4"/><circle cx="300" cy="120" r="3"/><circle cx="90" cy="40" r="3"/></g><g stroke="#16A36A" stroke-dasharray="3 4"><line x1="200" y1="75" x2="258" y2="60"/><line x1="200" y1="75" x2="130" y2="100"/></g></svg>'
    if kind == 1:
        return '<svg viewBox="0 0 400 150" preserveAspectRatio="xMidYMid meet"><g fill="#1B211D" stroke="#29332D"><rect x="40" y="40" width="80" height="70" rx="4"/><rect x="160" y="40" width="80" height="70" rx="4"/><rect x="280" y="40" width="80" height="70" rx="4" stroke="#16A36A"/></g><g stroke="#16A36A" stroke-width="2"><line x1="120" y1="75" x2="160" y2="75"/><line x1="240" y1="75" x2="280" y2="75"/></g><path d="M308 75l8 8 16-18" fill="none" stroke="#26C982" stroke-width="3"/></svg>'
    return '<svg viewBox="0 0 400 150" preserveAspectRatio="xMidYMid meet"><g fill="none" stroke="#29332D"><line x1="40" y1="120" x2="360" y2="120"/></g><g fill="#1B211D" stroke="#29332D"><rect x="60" y="80" width="40" height="40"/><rect x="130" y="60" width="40" height="60"/><rect x="200" y="45" width="40" height="75"/></g><rect x="270" y="20" width="40" height="100" fill="#16A36A"/></svg>'


# ---------------------------------------------------------------- pages
def build_home():
    sols = "".join(solution_block(s, i) for i, s in enumerate(SOLUTIONS))
    ch = "".join(
        f'<li class="ch-item reveal"><span class="ch-num">{i + 1:02d}</span><div><h3>{t}</h3><p>{d}</p></div></li>'
        for i, (t, d) in enumerate(CHALLENGES)
    )
    ticker_items = ["<em>More customers.</em>", "Better systems.", "<em>Less busywork.</em>", "Lead generation", "AI automation", "Business operations", "AI search visibility", "Customer experience"]
    ticker = "".join(f"<span>{t}</span>" for t in ticker_items) * 2
    posts = ""
    for i, p in enumerate(ARTICLES[:3]):
        feat = " feature" if i == 0 else ""
        posts += post_card(p, feat, i)

    body = f'''
<section class="hero">
  <div class="wrap">
    <div class="hero-grid">
      <div class="hero-in">
        <div class="hero-trust"><i></i>MARKETING <span class="sep"></span> AUTOMATION <span class="sep"></span> BUSINESS OPERATIONS</div>
        <h1 class="display"><span class="row">Turn More Opportunities</span> <span class="row">Into <span class="hl">Customers.</span></span> <span class="row soft">Build a Business That Runs Better.</span></h1>
        <p class="lead">From generating qualified leads and improving customer conversions to automating repetitive tasks and managing daily operations, Magneefy helps growing businesses make better use of their time, people, and resources.</p>
        <div class="hero-actions">
          <a href="contact.html" class="btn btn-primary btn-lg">Let’s Talk About Your Business {ARROW}</a>
          <a href="what-we-do.html" class="btn btn-ghost btn-lg">Explore What We Do</a>
        </div>
      </div>
      {hero_ecosystem()}
    </div>
    <div class="hero-foot">
      <div><strong>More customers</strong>Visibility and campaigns built around qualified enquiries.</div>
      <div><strong>Better systems</strong>Connected tools and automations that run reliably.</div>
      <div><strong>Less busywork</strong>Dependable support for the day-to-day operations.</div>
    </div>
  </div>
</section>

<div class="ticker" aria-hidden="true"><div class="ticker-track">{ticker}</div></div>

<section class="section" id="challenge">
  <div class="wrap challenge">
    <div class="challenge-intro reveal">
      <span class="eyebrow">The real business challenge</span>
      <h2 class="h2">Growing a Business Shouldn’t Mean <span class="hl">Managing Everything Yourself.</span></h2>
      <p class="lead">If any of these sound familiar, you’re not alone. They’re the most common reasons capable businesses grow slower than they should.</p>
    </div>
    <div>
      <ol class="ch-list">{ch}</ol>
      <div class="ch-close reveal">
        <p>These aren’t problems that need more busywork. They need better strategies, connected systems, and <span class="hl">consistent execution.</span></p>
        <a href="contact.html" class="btn btn-primary">Let’s Fix What’s Slowing You Down {ARROW}</a>
      </div>
    </div>
  </div>
</section>

<section class="section bg-2" id="solutions">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow reveal">What Magneefy does</span>
      <h2 class="h2 reveal d1">Practical Solutions for the Things That <span class="hl">Move Your Business Forward.</span></h2>
    </div>
    {sols}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow reveal">Why it works</span>
      <div class="reveal d1"><h2 class="h2">Growth and operations, <span class="hl">handled together.</span></h2>
      <p class="lead" style="margin-top:24px">More leads are only valuable if your business can respond to them. Better systems only matter if they help you win and serve more customers. Magneefy works across both, so improvements in one area aren’t undone by gaps in another.</p></div>
    </div>
    <div class="principles">
      <div class="principle reveal"><span class="n">01</span><h3>Outcomes before services</h3><p>We start with what needs to change in your business, then choose the work that will get you there.</p></div>
      <div class="principle reveal d1"><span class="n">02</span><h3>Connected, not piecemeal</h3><p>Marketing, follow-up, systems and operations designed to work as one customer journey.</p></div>
      <div class="principle reveal d2"><span class="n">03</span><h3>Honest measurement</h3><p>Clear tracking and plain-English reporting, so you always know what’s working and what isn’t.</p></div>
      <div class="principle reveal d3"><span class="n">04</span><h3>Documented &amp; yours</h3><p>Accounts, automations and processes are built in your name and documented so you’re never locked in.</p></div>
    </div>
  </div>
</section>

<section class="section bg-2">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow reveal">Our process</span>
      <h2 class="h2 reveal d1">A clear path from <span class="hl">bottleneck to better.</span></h2>
    </div>
    {process_section()}
    <div style="margin-top:56px" class="reveal"><a href="process.html" class="link-arrow">See how we work in detail {ARROW}</a></div>
  </div>
</section>

<section class="section">
  <div class="wrap">{founder_section()}</div>
</section>

<section class="section-tight bg-2">
  <div class="wrap">
    <div class="sec-head" style="margin-bottom:48px">
      <span class="eyebrow reveal">Who we work with</span>
      <h2 class="h3 reveal d1" style="font-size:clamp(1.6rem,3vw,2.6rem);letter-spacing:-.04em">Small and medium-sized businesses across the <span class="hl">US and UK</span> that are ready to grow with more structure.</h2>
    </div>
    {audience_strip()}
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow reveal">Insights</span>
      <div class="reveal d1" style="display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap"><h2 class="h2" style="max-width:14ch">Practical thinking for <span class="hl">growing businesses.</span></h2><a href="insights.html" class="link-arrow">All insights {ARROW}</a></div>
    </div>
    <div class="insights">{posts}</div>
  </div>
</section>

{cta_block('More Customers. Better Systems. <span class="hl">Less Busywork.</span>')}
'''
    page("index.html", "Magneefy | Digital Growth, Automation & Business Operations",
         "Magneefy helps growing US and UK businesses attract more customers, improve conversions, automate repetitive work and build efficient operations.",
         "home", body)


def build_solution(idx):
    s = SOLUTIONS[idx]
    nxt = SOLUTIONS[(idx + 1) % len(SOLUTIONS)]
    svcs = "".join(
        f'<div class="svc reveal d{j % 3}"><span class="n">{j + 1:02d}</span><h3>{e(n)}</h3><p>{d}</p></div>'
        for j, (n, d) in enumerate(s["services"])
    )
    outs = "".join(f'<li class="reveal"><span>{j + 1:02d}</span>{o}.</li>' for j, o in enumerate(s["outcomes"]))
    fit = "".join(f"<li>{x}</li>" for x in s["fit_for"])
    deliver = "".join(f"<li>{x}</li>" for x in s["deliver"])
    faq = "".join(f'<details><summary>{q}<i aria-hidden="true"></i></summary><p>{a}</p></details>' for q, a in s["faq"])
    faq_ld = ",".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}' % (jsonq(q), jsonq(a)) for q, a in s["faq"]
    )
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span><a href="what-we-do.html">What We Do</a><span>/</span>{s["short"]}</div>
    <div class="page-hero-grid">
      <div class="hero-in">
        <span class="eyebrow">Solution {s["num"]} · {s["name"]}</span>
        <h1>{s["headline_html"]}</h1>
        <p class="lead">{s["desc"]}</p>
        <div class="hero-actions" style="margin-top:36px">
          <a href="contact.html" class="btn btn-primary btn-lg">Let’s Talk About Your Business {ARROW}</a>
          <a href="#services" class="btn btn-ghost btn-lg">What’s included</a>
        </div>
      </div>
      <div class="reveal d2">{VISUALS[s["slug"]]()}</div>
    </div>
  </div>
</section>

<section class="section-tight bg-2">
  <div class="wrap story">
    <span class="eyebrow reveal">The approach</span>
    <div class="story-body reveal d1"><p class="big">{s["intro"]}</p></div>
  </div>
</section>

<section class="section" id="services">
  <div class="wrap">
    <div class="sec-head">
      <span class="eyebrow reveal">What’s included</span>
      <h2 class="h2 reveal d1">{len(s["services"])} services. <span class="hl">One joined-up plan.</span></h2>
    </div>
    <div class="svc-grid">{svcs}</div>
  </div>
</section>

<section class="section bg-2">
  <div class="wrap outcome-band">
    <div class="reveal">
      <span class="eyebrow">Business outcomes</span>
      <h2 class="h2" style="margin:26px 0 24px">What changes for <span class="hl">your business.</span></h2>
      <p class="lead">We agree on what success looks like before work begins, then track progress against it.</p>
    </div>
    <ol class="outcome-list">{outs}</ol>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="fit reveal">
      <div><h3>This is a fit if…</h3><ul>{fit}</ul></div>
      <div><h3>What you can expect</h3><ul>{deliver}</ul></div>
    </div>
  </div>
</section>

<section class="section bg-2">
  <div class="wrap outcome-band">
    <div class="reveal"><span class="eyebrow">Questions</span><h2 class="h2" style="margin-top:26px">Common <span class="hl">questions.</span></h2></div>
    <div class="faq reveal d1">{faq}</div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap">
    <a class="next-sol" href="{nxt["slug"]}.html">
      <div><small>NEXT SOLUTION · {nxt["num"]}</small><strong>{nxt["name"]}</strong></div>
      <span class="arrow">{ARROW_BIG}</span>
    </a>
  </div>
</section>

{cta_block(f'Let’s talk about <span class="hl">{s["short"].lower()}</span> for your business.')}
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}</script>
'''
    page(f'{s["slug"]}.html', f'{s["name"]} | Magneefy', s["desc"], "services", body)


def jsonq(s):
    import json
    return json.dumps(s)


def build_what_we_do():
    idx = "".join(
        f'''<a href="{s["slug"]}.html" class="reveal"><span class="outline-num">{s["num"]}</span>
      <div><small>{s["name"].upper()}</small><h3>{s["headline"]}</h3></div>
      <p>{s["desc"]}</p><span class="go">{ARROW}</span></a>'''
        for s in SOLUTIONS
    )
    sols = "".join(solution_block(s, i) for i, s in enumerate(SOLUTIONS))
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span>What We Do</div>
    <span class="eyebrow">What Magneefy does</span>
    <h1>Practical Solutions for the Things That <span class="hl">Move Your Business Forward.</span></h1>
    <p class="lead">Four connected areas of work. Use one on its own, or combine them so your marketing, systems and operations finally pull in the same direction.</p>
  </div>
</section>
<section class="section-tight" style="padding-top:0">
  <div class="wrap"><div class="sol-index">{idx}</div></div>
</section>
<section class="section bg-2"><div class="wrap">{sols}</div></section>
<section class="section">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow reveal">Ways to work together</span><h2 class="h2 reveal d1">Support shaped around <span class="hl">where you are.</span></h2></div>
    {models_html()}
  </div>
</section>
{cta_block()}
'''
    page("what-we-do.html", "What We Do | Magneefy",
         "Customer acquisition, AI automation, business operations support and websites that convert: practical solutions for growing businesses.",
         "services", body)


def models_html():
    return '''<div class="models">
  <div class="model reveal"><span class="k">PROJECT</span><h3>Defined projects</h3><p>A clear scope, timeline and deliverable. Ideal for a new website, a CRM setup, an automation build or a marketing launch.</p><ul><li>Fixed scope agreed upfront</li><li>Documented handover</li><li>Optional support afterwards</li></ul></div>
  <div class="model feat reveal d1"><span class="k">ONGOING PARTNERSHIP</span><h3>Monthly growth &amp; systems</h3><p>Continuous marketing, automation and optimisation, with regular reporting and a roadmap that evolves with your business.</p><ul><li>Prioritised monthly roadmap</li><li>Regular performance reviews</li><li>One partner across channels</li></ul></div>
  <div class="model reveal d2"><span class="k">DEDICATED SUPPORT</span><h3>Operations &amp; assistance</h3><p>Reliable virtual assistance and operations management on an agreed number of hours or set responsibilities.</p><ul><li>Agreed hours or responsibilities</li><li>US &amp; UK business hours</li><li>Scales up or down as needed</li></ul></div>
</div>'''


def build_about():
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span>About</div>
    <span class="eyebrow">About Magneefy</span>
    <h1>Grow Smarter. <span class="hl">Operate Better.</span></h1>
    <p class="lead">Magneefy helps growing businesses attract more customers, improve conversions, automate repetitive work, and build efficient business operations.</p>
  </div>
</section>

<section class="section-tight bg-2">
  <div class="wrap story">
    <span class="eyebrow reveal">Why we exist</span>
    <div class="story-body reveal d1">
      <p class="big">Growing businesses are often stuck between two problems: not enough of the right customers, and not enough time or structure to serve the ones they have.</p>
      <p>Most agencies solve one side. A marketing agency brings in leads that nobody follows up on. An operations consultant streamlines a business that still struggles to grow. A freelancer completes tasks without seeing how they connect.</p>
      <p>Magneefy was built to close that gap. We combine digital marketing, AI automation, business operations support and customer experience under one roof, so the way you attract customers and the way you serve them are designed together.</p>
    </div>
  </div>
</section>

<section class="section"><div class="wrap">{founder_section(full=True)}</div></section>

<section class="section bg-2">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow reveal">How we’re different</span><h2 class="h2 reveal d1">Less noise. <span class="hl">More execution.</span></h2></div>
    <div class="contrast reveal">
      <div><h3>What you won’t get</h3><ul><li>Vanity metrics and jargon-heavy reports</li><li>Tools bought, then never connected</li><li>Accounts and systems you don’t own</li><li>One-size-fits-all packages</li><li>Advice without implementation</li></ul></div>
      <div><h3>What you will get</h3><ul><li>Clear goals tied to business outcomes</li><li>Systems that work together, documented</li><li>Everything built in your name</li><li>Recommendations based on your business</li><li>Hands-on delivery, start to finish</li></ul></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow reveal">What we value</span><h2 class="h2 reveal d1">The standards behind <span class="hl">every engagement.</span></h2></div>
    <div class="principles">
      <div class="principle reveal"><span class="n">01</span><h3>Reliability</h3><p>We do what we say, when we say. Dependable execution is the foundation of everything else.</p></div>
      <div class="principle reveal d1"><span class="n">02</span><h3>Clarity</h3><p>Plain language, honest assessments and transparent reporting, including when something isn’t working.</p></div>
      <div class="principle reveal d2"><span class="n">03</span><h3>Efficiency</h3><p>We look for the simplest solution that delivers the outcome, not the most impressive-sounding one.</p></div>
      <div class="principle reveal d3"><span class="n">04</span><h3>Ownership</h3><p>We treat your business like it matters, because your results are the only measure of our work.</p></div>
    </div>
  </div>
</section>

<section class="section-tight bg-2">
  <div class="wrap">
    <div class="sec-head" style="margin-bottom:48px"><span class="eyebrow reveal">Who we work with</span><h2 class="h3 reveal d1" style="font-size:clamp(1.6rem,3vw,2.6rem);letter-spacing:-.04em">Founders, owners and management teams who value <span class="hl">efficiency, measurable results and dependable support.</span></h2></div>
    {audience_strip()}
  </div>
</section>
{cta_block()}
'''
    page("about.html", "About Magneefy | Founded by Jeffery Odiba",
         "Magneefy combines digital marketing, AI automation and business operations support so growing businesses can grow smarter and operate better.",
         "about", body)


def build_process():
    detail = [
        ("Discover", "Week 1", "A focused conversation about your business, goals, customers and current tools, followed by a look at your existing marketing, systems and workflows.", ["Discovery call", "Access to relevant accounts and tools", "Review of current marketing, systems and processes"]),
        ("Diagnose & Plan", "Week 1–2", "We identify the bottlenecks costing you the most time and opportunity, then translate them into a prioritised roadmap with clear scope and success measures.", ["Findings summary in plain English", "Prioritised roadmap: quick wins first", "Clear scope, timeline and investment"]),
        ("Build & Implement", "Week 2 onward", "We set up the campaigns, automations, websites and support structures in the roadmap, testing each one and documenting how it works.", ["Builds in your accounts, owned by you", "Testing before anything goes live", "Documentation and team walkthroughs"]),
        ("Run, Measure & Improve", "Ongoing", "Once live, we manage, monitor and report. Each review leads to the next set of improvements so results compound over time.", ["Regular reporting against agreed goals", "Monitoring and fixes", "A roadmap that evolves with the business"]),
    ]
    rows = ""
    for i, (t, w, d, items) in enumerate(detail):
        li = "".join(f"<li>{x}</li>" for x in items)
        rows += f'''<div class="post-row reveal"><span class="cat">Step {i + 1:02d}<br><span class="muted" style="letter-spacing:.1em">{w}</span></span>
      <div><h3>{t}</h3><p>{d}</p></div>
      <div class="meta" style="text-align:left"><ul style="list-style:none;padding:0;margin:0">{"".join(f'<li style="padding:6px 0;border-top:1px solid var(--line)">{x}</li>' for x in items)}</ul></div></div>'''
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span>Our Process</div>
    <span class="eyebrow">Our process</span>
    <h1>A clear path from <span class="hl">bottleneck to better.</span></h1>
    <p class="lead">No guesswork and no unnecessary complexity. A structured way of understanding your business, fixing what matters most first, and improving continuously.</p>
  </div>
</section>
<section class="section-tight" style="padding-top:0"><div class="wrap">{process_section()}</div></section>
<section class="section bg-2">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow reveal">In detail</span><h2 class="h2 reveal d1">What happens <span class="hl">at each stage.</span></h2></div>
    <div class="post-list">{rows}</div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="sec-head"><span class="eyebrow reveal">Ways to work together</span><h2 class="h2 reveal d1">Support shaped around <span class="hl">where you are.</span></h2></div>
    {models_html()}
  </div>
</section>
<section class="section bg-2">
  <div class="wrap outcome-band">
    <div class="reveal"><span class="eyebrow">Working together</span><h2 class="h2" style="margin-top:26px">How we keep things <span class="hl">running smoothly.</span></h2></div>
    <div class="faq reveal d1">
      <details><summary>How do we communicate?<i aria-hidden="true"></i></summary><p>We agree on channels and rhythm at the start, usually email or Slack for day-to-day work, plus scheduled check-ins for reviews and planning.</p></details>
      <details><summary>Do you work in our time zone?<i aria-hidden="true"></i></summary><p>We work with businesses in the US and UK and schedule support and meetings around your business hours.</p></details>
      <details><summary>Who owns the accounts and systems you build?<i aria-hidden="true"></i></summary><p>You do. Ad accounts, automations, websites and documentation are set up in your name so you keep full control.</p></details>
      <details><summary>What do you need from us to get started?<i aria-hidden="true"></i></summary><p>A discovery conversation, access to the relevant tools, and a point of contact for questions. We keep the time we need from you to a minimum.</p></details>
    </div>
  </div>
</section>
{cta_block()}
'''
    page("process.html", "Our Process | Magneefy",
         "Discover, diagnose, build and improve: how Magneefy works with growing businesses to fix bottlenecks and build better systems.",
         "process", body)


def build_insights():
    feat = ARTICLES[0]
    rows = "".join(
        f'''<a class="ins-row reveal" href="{p["url"]}"><img src="{p["image"]}" alt="" loading="lazy" width="1200" height="675">
      <div><span class="cat">{p["category"]}</span><h3>{p["title"]}</h3><p>{p["excerpt"]}</p></div>
      <div class="meta">{p["read"]}<span class="link-arrow">Read article {ARROW}</span></div></a>'''
        for p in ARTICLES[1:]
    )
    rows = f'''<a class="ins-feature reveal" href="{feat["url"]}"><img src="{feat["image"]}" alt="{e(feat["image_alt"])}" width="1200" height="675">
      <div><span class="cat">Featured · {feat["category"]}</span><h2>{feat["title"]}</h2><p>{feat["excerpt"]}</p>
      <span class="meta">{feat["read"]}</span><span class="btn btn-primary">Read article {ARROW}</span></div></a>
    <div class="post-list" style="margin-top:clamp(48px,6vw,80px)">{rows}</div>'''
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span>Insights</div>
    <span class="eyebrow">Insights</span>
    <h1>Practical thinking for <span class="hl">growing businesses.</span></h1>
    <p class="lead">Straightforward guidance on marketing, AI search, automation and operations, written for owners and teams who want to act on it.</p>
  </div>
</section>
<section class="section-tight" style="padding-top:0">
  <div class="wrap">{rows}</div>
</section>
<section class="section bg-2">
  <div class="wrap outcome-band">
    <div class="reveal"><span class="eyebrow">Stay informed</span><h2 class="h2" style="margin-top:26px">Get new insights <span class="hl">in your inbox.</span></h2></div>
    <div class="reveal d1">
      <p class="lead" style="margin-bottom:30px">One useful email when new articles publish. No filler, and you can unsubscribe at any time.</p>
      <form class="subscribe" novalidate><label class="sr-only" for="sub-email">Email address</label><input id="sub-email" type="email" placeholder="you@company.com" autocomplete="email"><button type="submit">Subscribe {ARROW}</button></form>
      <p class="sub-msg" aria-live="polite"></p>
    </div>
  </div>
</section>
{cta_block()}
'''
    page("insights.html", "Insights | Magneefy",
         "Guidance on digital marketing, AI search optimization, automation and business operations for growing businesses.",
         "insights", body)


def build_contact():
    needs = ["Customer acquisition", "AI automation", "Virtual assistance & operations", "Website & content", "Not sure yet"]
    picks = "".join(f'<label><input type="checkbox" name="needs" value="{n}"><span>{n}</span></label>' for n in needs)
    body = f'''
<section class="page-hero">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span>/</span>Contact</div>
    <span class="eyebrow">Contact</span>
    <h1>Let’s Talk About <span class="hl">Your Business.</span></h1>
    <p class="lead">Tell us what’s slowing you down or where you want to grow. We’ll reply with practical next steps, not a sales script.</p>
  </div>
</section>
<section class="section-tight" style="padding-top:0">
  <div class="wrap contact">
    <aside class="contact-side reveal">
      <h3>What happens next</h3>
      <ol class="next-steps">
        <li><div><b>We review your enquiry</b><span>We read every message properly and reply within one business day.</span></div></li>
        <li><div><b>A short discovery call</b><span>A focused conversation about your goals, challenges and current setup.</span></div></li>
        <li><div><b>Clear recommendations</b><span>A practical plan with scope and next steps, so you can decide with confidence.</span></div></li>
      </ol>
      <div class="direct">
        <span class="eyebrow plain" style="margin-bottom:10px;display:block">Prefer email?</span>
        <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>
        <p>Supporting businesses across US and UK business hours.</p>
      </div>
    </aside>
    <div class="form-wrap reveal d1">
      <form id="contact-form" class="form" novalidate data-endpoint="" data-mailto="{CONTACT_EMAIL}">
        <div class="field" data-required><label for="f-name">Your name <em>*</em></label><input id="f-name" name="name" autocomplete="name" placeholder="Full name"><span class="err">Please enter your name.</span></div>
        <div class="field" data-required><label for="f-email">Work email <em>*</em></label><input id="f-email" name="email" type="email" autocomplete="email" placeholder="you@company.com"><span class="err">Please enter a valid email address.</span></div>
        <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization" placeholder="Company name"></div>
        <div class="field"><label for="f-site">Website</label><input id="f-site" name="website" autocomplete="url" placeholder="yourbusiness.com"></div>
        <fieldset class="field full"><legend>What can we help with?</legend><div class="pick">{picks}</div></fieldset>
        <div class="field full"><label for="f-stage">Where is your business today?</label>
          <select id="f-stage" name="stage"><option value="">Select one</option><option>Solo founder / owner-operator</option><option>Small team (2–10)</option><option>Growing business (11–50)</option><option>Established business (50+)</option></select></div>
        <div class="field full" data-required><label for="f-msg">Tell us about your business <em>*</em></label><textarea id="f-msg" name="message" placeholder="What you do, what’s slowing you down, and what you’d like to achieve."></textarea><span class="err">Please add a short message.</span></div>
        <div class="form-foot"><p>We’ll only use your details to respond to your enquiry.</p><button type="submit" class="btn btn-primary btn-lg">Send Enquiry {ARROW}</button></div>
      </form>
      <div class="form-success" role="status">
        <span class="eyebrow">Message ready</span>
        <h3 style="margin-top:20px">Thanks. We’ll be in touch shortly.</h3>
        <p>If your email app didn’t open, please send your message directly to <a class="hl" href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>
      </div>
    </div>
  </div>
</section>
'''
    page("contact.html", "Contact | Magneefy",
         "Talk to Magneefy about growing your business, automating repetitive work and building better operations.",
         "contact", body)


def build_misc():
    fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="6" fill="#0B0D0C"/><g transform="translate(4 4)">' + MARK.replace('<svg class="mark" viewBox="0 0 24 24" aria-hidden="true">', '').replace('</svg>', '') + '</g></svg>'
    (ROOT / "assets/img/favicon.svg").write_text(fav, encoding="utf-8")
    urls = ["index.html", "what-we-do.html"] + [s["slug"] + ".html" for s in SOLUTIONS] + ["about.html", "process.html", "insights.html", "contact.html"] + [a["url"] for a in ARTICLES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f'  <url><loc>{SITE_URL}/{re.sub(r"index[.]html$", "", u)}</loc></url>\n' for u in urls) + "</urlset>\n"
    (ROOT / "sitemap.xml").write_text(sm, encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print("wrote favicon, sitemap.xml, robots.txt")


SOL_BY_SLUG = {s["slug"]: s for s in SOLUTIONS}


def post_card(p, feat="", i=0):
    return f"""<a class="post{feat} reveal d{i % 4}" href="{p["url"]}">
      <div class="post-art"><img src="{p["image"]}" alt="" loading="lazy" width="1200" height="675"></div>
      <span class="cat">{p["category"]}</span><h3>{p["title"]}</h3><p>{p["excerpt"]}</p>
      <span class="meta"><span>{p["read"]}</span><span class="link-arrow">Read {ARROW}</span></span></a>"""


def build_articles():
    for a in ARTICLES:
        A_path = f'insights/{a["slug"]}/index.html'
        (ROOT / a["image"]).write_text(A.art(a["slug"]), encoding="utf-8")
        svc = SOL_BY_SLUG[a["service"]]
        toc = "".join(f'<li><a href="#{hid}">{e(t)}</a></li>' for hid, t in a["toc"])
        related = "".join(post_card(ART_BY_SLUG[r], "", i) for i, r in enumerate(a["related"]))
        url = f'{SITE_URL}/{a["url"]}'
        ld = {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": a["title"],
                    "description": a["description"],
                    "image": f'{SITE_URL}/{a["image"]}',
                    "mainEntityOfPage": url,
                    "articleSection": a["category"],
                    "author": {"@type": "Organization", "name": "Magneefy", "url": SITE_URL},
                    "publisher": {"@type": "Organization", "name": "Magneefy", "url": SITE_URL,
                                  "founder": {"@type": "Person", "name": "Jeffery Odiba"}},
                    **({"datePublished": a["date"]} if a.get("date") else {}),
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE_URL + "/"},
                        {"@type": "ListItem", "position": 2, "name": "Insights", "item": SITE_URL + "/insights.html"},
                        {"@type": "ListItem", "position": 3, "name": a["title"], "item": url},
                    ],
                },
            ],
        }
        body = f"""
<section class="page-hero art-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><a href="insights.html">Insights</a><span>/</span>{a["category"]}</nav>
    <div class="hero-in">
      <span class="eyebrow">{a["category"]} · {a["read"]}</span>
      <h1 class="art-title">{e(a["title"])}</h1>
      <p class="lead">{a["description"]}</p>
      <div class="art-byline"><span class="mono-badge">M</span><div><b>Magneefy Insights</b><small>Business growth, digital marketing &amp; operations</small></div></div>
    </div>
  </div>
</section>
<div class="wrap"><figure class="art-figure reveal"><img src="{a["image"]}" alt="{e(a["image_alt"])}" width="1200" height="675"></figure></div>

<section class="section-tight">
  <div class="wrap art-layout">
    <aside class="art-toc">
      <span class="eyebrow plain">On this page</span>
      <ol>{toc}</ol>
      <a href="{svc["slug"]}.html" class="art-svc"><small>RELATED SOLUTION · {svc["num"]}</small><b>{svc["name"]}</b><span class="link-arrow">Explore {ARROW}</span></a>
    </aside>
    <article class="prose">
      {a["html"]}
      <div class="art-cta">
        <p>{a["cta_text"].replace("'", "’")}</p>
        <div class="art-cta-actions">
          <a href="contact.html" class="btn btn-primary btn-lg">{a["cta"].replace("'", "’")} {ARROW}</a>
          <a href="{svc["slug"]}.html" class="link-arrow">{svc["short"]} services {ARROW}</a>
        </div>
      </div>
    </article>
  </div>
</section>

<section class="section bg-2">
  <div class="wrap">
    <div class="sec-head" style="margin-bottom:56px"><span class="eyebrow reveal">Keep reading</span>
      <div class="reveal d1" style="display:flex;justify-content:space-between;align-items:flex-end;gap:24px;flex-wrap:wrap"><h2 class="h2">Related <span class="hl">insights.</span></h2><a href="insights.html" class="link-arrow">All insights {ARROW}</a></div></div>
    <div class="insights insights-2">{related}</div>
  </div>
</section>
{cta_block()}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
"""
        page(A_path, f'{a["seo_title"]} | Magneefy', a["description"], "insights", body,
             extra_head=f'<meta property="og:image" content="{SITE_URL}/{a["image"]}">')


if __name__ == "__main__":
    build_home()
    build_what_we_do()
    for i in range(len(SOLUTIONS)):
        build_solution(i)
    build_about()
    build_process()
    build_insights()
    build_contact()
    build_articles()
    build_misc()
