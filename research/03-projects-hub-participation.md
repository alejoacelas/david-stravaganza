# Idea 3: Participation and support for the projects hub

## Conclusion

This is the easiest of David's ideas to finish: about one to two weeks of work for an outside builder. It is also the least ambitious, and the money it raises will be close to zero for now.

- **Traffic.** The hub had 121 pageviews from 84 distinct IPs in September 2026 ([his engagement report](https://reinstein-site-engagement.netlify.app/)).
- **What the asks should be.** Non-money asks will do more than a tip jar: try this, report a bug, suggest a gig, collaborate, book the band, commission a tool. Money asks matter less.
- **The two support routes are cheap to set up:**
  - **The Unjournal:** a link to its existing Donorbox page at [info.unjournal.org/donate](https://info.unjournal.org/donate/).
  - **David personally:** one fee-free platform. The best fits are Ko-fi or Liberapay, or GitHub Sponsors if he qualifies.
- **What to copy.** Andrew Kelley's sponsor page shows the separation in two sentences. Kelley is president of the Zig Software Foundation, a 501(c)(3). His page says: "If you want to donate to the Zig Software Foundation, a 501(c)(3) not-for-profit: … If you want to donate to me as an individual: …" ([github.com/sponsors/andrewrk](https://github.com/sponsors/andrewrk)).
- **"Tested wording" cannot mean an A/B test.** At this traffic, a click-rate test would take one to two years to reach a result (see below).
  - Instead, test wording on the higher-traffic destination sites, with a handful of target readers, or by tracking replies.
  - Or accept that the wording is chosen on judgment.
- **Biggest risk: labelling each card's owner.** Several cards are Unjournal-built or Unjournal-hosted. A personal tip button next to them would blur the line David most wants kept. Each card needs an owner label (Unjournal, personal or mixed) before any ask goes on it, and only David can assign it.
- **Lawyer or accountant.** One short review is worth paying for before the personal money route goes live (see "Rules").

## What exists today

I fetched https://projects.davidreinstein.org/ on 3 Nov 2026.

- **Cards.** 31 cards in six sections: Music 5, Games and everyday tools 5, Ideas and proposals 4, Research and giving 7, Teaching 3, Unjournal tools 7.
  - Each card has a screenshot, a type label ("App", "Proposal"…), a title, a one-line description and sometimes "Source" or extra links.
  - **No card carries an ask.**
- **Ways to respond today:**
  - Hypothes.is annotation.
  - A footer `mailto:daaronr@gmail.com`.
  - The "Ideas and proposals" section says "Feedback and collaborators welcome."
  - An [Offerings page](https://projects.davidreinstein.org/offerings/) lists paid personal work: bands, brass sessions, custom tools.
- **Missing.** There is no donate or support link, newsletter, sign-up form or RSS/Atom feed (`/feed.xml` and `/rss.xml` return 404). The footer shows only "Updated 28 October 2026".
- **Measurement already in place.**
  - Every card link carries `data-engagement="<slug>"`.
  - An inline script POSTs clicks to `/__engagement/action/<slug>`, skipping visitors who send Do Not Track or Global Privacy Control.
  - A Netlify edge function counts the clicks into an aggregate store ([example source in daaronr/impact-directory](https://github.com/daaronr/impact-directory/blob/main/netlify/edge-functions/engagement.ts)).
  - Ask clicks can be counted with this existing counter by giving each ask its own label. No new analytics are needed.
- **Hosting.** Netlify (from the response headers). I could not find the hub's own source among the public repos at github.com/daaronr (searched by title text and engagement path). It may be private. Unverified.
- **Who owns which card:**
  - **Clearly Unjournal (7):** the Unjournal tools section.
  - **Unjournal-adjacent (5):**
    - Who's available is hosted on info.unjournal.org.
    - The Meeting scheduler was "built for Unjournal team meetings".
    - The Prioritization ML Lab was made for Unjournal's pipeline.
    - Just Ask the Model is co-authored Unjournal-related research.
    - The AI-wealth model sits on a `uj-` Netlify subdomain.
  - **Personal (about 19):** all the rest.
- **The Unjournal's existing route.** [info.unjournal.org/donate](https://info.unjournal.org/donate/) says "501(c)(3) nonprofit • All donations tax-deductible" and links to [Donorbox](https://donorbox.org/the-unjournal-donations).
- **Destination traffic (Sep–Oct 2026).** Most destination sites get more traffic than the hub: AI jazz tune trial 1,189 pageviews, AI-wealth model 828, Library of Things 665, Complainments 333 ([same report](https://reinstein-site-engagement.netlify.app/)).

## Options

### Personal support route

| Option | Fees | Static site | Notes |
|---|---|---|---|
| [Ko-fi](https://ko-fi.com/gold) | 0% on tips (free plan); 5% on memberships and shop unless Gold at $12/month | Link or script-tag button ([widget docs](https://help.ko-fi.com/hc/en-us/articles/360018381678-Ko-fi-tip-widget)) | Pays straight into his PayPal or Stripe ([payouts](https://help.ko-fi.com/hc/en-us/articles/115003980153)). Handles one-off and monthly. |
| [GitHub Sponsors](https://docs.github.com/en/sponsors/getting-started-with-github-sponsors/about-github-sponsors) | 0% from personal accounts; up to 6% from organizations | Link | Requires open-source contribution, Stripe Connect and a W-9 ([setup](https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/setting-up-github-sponsors-for-your-personal-account)). Whether he qualifies is a judgment call. Simon Willison's [model](https://github.com/sponsors/simonw) is one of the best examples. |
| [Liberapay](https://liberapay.com/about/faq) | No platform fee; about 3% Stripe or 5% PayPal | Link | Built for recurring gifts; one-off gifts "aren't properly supported yet". US and UK [well supported](https://liberapay.com/about/global). Kelley uses it. |
| [Buy Me a Coffee](https://help.buymeacoffee.com/en/articles/8105744-how-to-calculate-charges-on-your-payment) | 5% plus Stripe plus 0.5–1% extras | Link | Costs more than Ko-fi for the same thing. |
| [Patreon](https://support.patreon.com/hc/en-us/articles/11111747095181-Creator-fees-overview) | 10% for new creators plus processing | Link | Expects regular patron content, which means weekly attention (fails E). Gwern ([/me](https://gwern.net/me)) and Andy Matuschak ([andymatuschak.org](https://andymatuschak.org/)) use it, but both make this work their main living. |
| [Stripe Payment Links](https://stripe.com/us/pricing) | 2.9% + 30¢ (US cards) | Hosted URL | He keeps all records himself; no donor-facing page. Fine, but more work for nothing extra. |
| [Open Source Collective](https://docs.oscollective.org/welcome-and-introduction-to-osc/fees) | 10% host fee | Link | Open-source projects only. A 501(c)(6), so gifts are not deductible ([oscollective.org](https://oscollective.org/)). Open Collective Foundation, the 501(c)(3) host, [dissolved at the end of 2024](https://opencollective.com/foundation/updates/announcement-we-are-dissolving-open-collective-foundation-at-the-end-of-this-year). |
| Offerings page (exists) | n/a | Already live | Paid work is the personal money route with the most potential. Each personal card can point "want one like this?" at it. |

### Unjournal support route

Keep Donorbox and link to the existing page. Donorbox Standard is free to the nonprofit, with fees of 2.95–3.95% ([pricing](https://donorbox.org/pricing)). How that range splits between Donorbox and the card processor is unverified.

Alternatives exist and are not worth switching to for this:
- [Every.org](https://www.every.org/pricing): 0% platform fee, cards 2.2% + 30¢.
- [Givebutter](https://givebutter.com/pricing): 0% with donor tips, otherwise 3%.

Either alternative would be an Unjournal decision, not a hub one.

### Feed and sign-up

| Option | Cost | Static site | Sends email from the feed automatically? |
|---|---|---|---|
| Build-time Atom/RSS feed from a changelog file | Free | Yes | No; reaches feed readers only |
| [Buttondown](https://buttondown.com/pricing) | Free to 100 subscribers; RSS-to-email is a [$9/month add-on](https://docs.buttondown.com/rss-to-email) | Plain HTML form posting to `embed-subscribe` ([docs](https://docs.buttondown.com/building-your-subscriber-base)) | Yes, paid. Can send a monthly digest or a draft for review. |
| [Substack](https://substack.com/going-paid) | Free (10% only on paid subscriptions) | Embed or iframe form | Unverified; he would post by hand |
| [Kit](https://kit.com/pricing) | Free to 10,000 subscribers; RSS campaigns only from $33/month | Form | Paid |
| [MailerLite](https://www.mailerlite.com/pricing) | Free to 250 subscribers | Form | Premium only ([features](https://www.mailerlite.com/features/rss-to-email)) |
| [Mailchimp](https://mailchimp.com/pricing/marketing/) | Free to 250 contacts and 500 emails/month | Form | Whether the free plan includes RSS campaigns is unverified |
| [follow.it](https://follow.it/pricing) | Free (with ads); $5/month removes ads | Form | Yes, free. Least control over branding and data; export unverified. |
| [Netlify Forms](https://docs.netlify.com/manage/forms/setup/) | Free; legacy plans limited to [100 submissions per site per month](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-legacy-plans/legacy-pricing-plans/) | `data-netlify="true"` | No; only collects addresses |
| A "now" page ([convention](https://nownownow.com/about), [Sivers's](https://sive.rs/now)) | Free | Yes | No; needs an occasional manual edit |

FeedBurner email has been [dead since 2021](https://support.google.com/feedburner/answer/10483501).

## Scores against David's criteria

Scale: 1 is poor, 5 is strong. A = public material only, B = first version testable, C = real payoff, D = Unjournal and personal kept visibly separate, E = cheap and low-maintenance.

| Option | A | B | C | D | E | Comment |
|---|---|---|---|---|---|---|
| **David's version as written** (ask per card, feed, sign-up, two routes, tested wording) | 5 | 4 | 2 | 3 | 4 | Uses only his own public pages. B is easy except "tested wording" (see below). D depends entirely on labelling each card's owner. |
| **Recommended version** (owner label per card; mostly non-money asks; Ko-fi or Liberapay plus the existing Donorbox link on one support page; build-time Atom feed; Buttondown form) | 5 | 5 | 3 | 5 | 5 | Every part can be checked by looking at the page. |
| Ko-fi | 5 | 5 | 2 | 4 | 5 | Free tips, no review. Its branding is casual, which is good for separation. |
| GitHub Sponsors | 5 | 4 | 2 | 4 | 5 | Free, but eligibility review and a W-9. Fits his developer audience. |
| Liberapay | 5 | 5 | 2 | 5 | 5 | Kelley's precedent; recurring gifts only. |
| Buy Me a Coffee | 5 | 5 | 2 | 4 | 5 | Higher fees than Ko-fi for the same thing. |
| Patreon | 5 | 4 | 2 | 4 | 2 | Expects content for patrons. |
| Open Source Collective | 5 | 3 | 1 | 3 | 4 | 10% fee, open source only, review process. |
| Fiscal sponsor for a personal project | 5 | 2 | 2 | 4 | 3 | Only worth it if one project needs tax-deductible gifts. Gifts earmarked for him personally remain non-deductible ([IRS Pub 526](https://www.irs.gov/publications/p526)). |
| Donorbox link for The Unjournal (exists) | 5 | 5 | 3 | 5 | 5 | Nothing to build; it just needs linking. |
| Build-time Atom feed | 5 | 5 | 2 | 5 | 5 | Free; updates whenever he edits the changelog. |
| Buttondown free plus monthly RSS digest ($9/month) | 5 | 5 | 3 | 5 | 4 | Sign-ups are useful long after a tip would be. The digest removes the weekly task. |
| Substack | 5 | 5 | 3 | 4 | 3 | Free, but he has to write the posts. |
| follow.it | 5 | 5 | 2 | 5 | 5 | Free email from the feed; ads and less control. |

## Rules on keeping the money separate (practical level; not legal advice)

- **Personal gifts aren't deductible.** "You can't deduct contributions to specific individuals" ([Pub 526](https://www.irs.gov/publications/p526)). The personal route should say plainly: "Gifts to me personally are not tax-deductible and do not support The Unjournal."
  - The IRS's required non-deductibility notice formally covers certain exempt organizations, not individuals ([IRS](https://www.irs.gov/charities-non-profits/solicitation-notice)).
  - Its safe-harbour style is still a good model: same type size as the ask, in its own sentence ([IRS fundraising guide](https://www.irs.gov/pub/irs-tege/atg_fundraising.pdf)).
- **The real risk is on The Unjournal's side.** A 501(c)(3)'s earnings must not inure to insiders, and the organization must not serve private interests ([IRS](https://www.irs.gov/charities-non-profits/charitable-organizations/inurement-private-benefit-charitable-organizations)).
  - As co-founder he is probably a "disqualified person" (an insider) for excess-benefit purposes ([IRS intermediate sanctions](https://www.irs.gov/charities-non-profits/charitable-organizations/intermediate-sanctions)).
  - In practice: The Unjournal's site, mailing lists, donor data and staff time should not send people to his personal tip route.
  - The personal route should not use The Unjournal's name to raise money.
  - Unjournal-owned cards should carry only Unjournal asks.
  - Personal-route links should live on his personal domain only, not on unjournal.org pages.
  - I found no IRS page specifically on a founder's personal tip jar. These points apply the general rule.
- **Ask a lawyer or accountant before the personal money route goes live:**
  1. Whether linking between the personal hub and The Unjournal's donate page creates any private-benefit concern, and how it should appear in The Unjournal's conflict-of-interest policy.
  2. Whether tips are gifts or self-employment income for him, given that GitHub and Stripe report income to the IRS on 1099-K.
  3. UK tax, given his Exeter ties.
  4. Whether any state requires charitable-solicitation registration for The Unjournal ask as placed on his personal site.

## Steps to the milestone

1. **Owner labels (half a day, needs David).**
   - Add an `owner` field to each of the 31 cards: Unjournal, personal or mixed.
   - Pre-fill it from the evidence above and have David confirm the 5 Unjournal-adjacent cards.
   - Show the label visibly on each card.
2. **One ask per card (2–3 days).**
   - Add an `ask` field (verb, short sentence, target link), drafted per project from the destination site's own content.
   - Use mostly non-money asks:
     - "Suggest a gig" (Exeter calendar)
     - "Report a wrong figure" (Math Estimator, Impact Directory)
     - "Vote before you look" (AI jazz trial)
     - "Want one like this? See Offerings" (tools)
     - "Collaborate on this proposal" (Ideas)
   - Unjournal-owned cards point to Unjournal asks: suggest a paper, join a workshop, donate via Donorbox.
   - Give each ask its own engagement label, e.g. `ask-blues-flow`, so the existing counter records clicks.
3. **Support page `/support/` (1 day).**
   - Two clearly separate blocks, modelled on Kelley's wording.
     - **Block one, The Unjournal:** "a 501(c)(3); tax-deductible", linking to Donorbox.
     - **Block two, David personally:** "not tax-deductible; does not fund The Unjournal", linking to Ko-fi or Liberapay, plus Offerings for paid work.
   - Link the page from the header and footer, not from every card. Money then appears in one place where the separation is explained.
4. **Feed and sign-up (1 day).**
   - Add a `changelog.yml` (date, project, one line), from which the build writes `/feed.xml` (Atom) and an "Updates" list on the hub.
   - Add a Buttondown form, free to 100 subscribers.
   - Optionally turn on RSS-to-email as a monthly digest ($9/month) so subscribers get mail without David writing anything.
   - Adding a changelog line whenever he ships something is the only ongoing task.
5. **Check the milestone.**
   - A script fails the build if any card lacks an `owner` or an `ask`, or if a personal-owned card links to Donorbox (or an Unjournal card to Ko-fi).
   - `/feed.xml` validates (W3C feed validator).
   - A test sign-up arrives in Buttondown.
   - Both support links resolve.

## One step past the milestone: testing the wording

- **An A/B test on the hub is not feasible.** Detecting a click rate going from 2% to 4% needs about 1,140 visitors per variant (two-sided test, 5% significance, 80% power; my calculation). That is about 2,300 visitors, roughly 19 months at the hub's current traffic. Detecting a jump from 1% to 2% needs about 4,600 visitors.
- **Feasible alternatives, cheapest first:**
  1. **Five-person read-through.** Show five people from the intended audience the card and support page. Ask them what each button does with their money and who receives it. Any confusion between The Unjournal and David personally is a fail. This directly tests criterion D.
  2. **Test on the higher-traffic destinations.** Put the same ask on the AI jazz tune trial (about 1,200 pageviews a month) and the AI-wealth model (about 800). Alternate two wordings by week, using the existing engagement labels. Even there, expect only large effects to show.
  3. **Count outcomes, not clicks.** Monthly, record replies, gig suggestions, sign-ups and Offerings enquiries per ask. These are few enough to read by hand.
- David ran EA Market Testing messaging trials, so he will know these limits. The point is to state them in the plan up front rather than promise "tested wording".

## Biggest risk

**Blurred ownership, not technology.**
- Too many money asks next to Unjournal-branded cards could make it look like the nonprofit funds him, or like tips fund the nonprofit. Mitigations: the owner labels, the build check, and one support page.
- **Second risk:** the payoff is small. With current traffic, expect a few sign-ups and a few enquiries a month, and tips near zero. This is my estimate; there is no comparable public data.
- **Third risk:** the changelog goes stale and the feed dies. Keep it to one line per shipped change, and let the build fail if the newest entry is older than 90 days, which forces a decision rather than silent rot.

## Cheapest stack

- **Data:** the existing hub build plus a `projects.yml` holding owner and ask, and a `changelog.yml`.
- **Feed:** Atom, written at build time.
- **Sign-up:** Buttondown free form.
- **Personal route:** Ko-fi free (or Liberapay).
- **Unjournal route:** the existing Donorbox link.
- **Measurement:** the existing engagement counter.
- **Cost:** $0 a month, or $9 a month if he wants feed updates emailed automatically.
- **One-time:** a short paid consult with a nonprofit lawyer or CPA on the four questions above. Price unverified.
