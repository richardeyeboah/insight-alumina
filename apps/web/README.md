# Insight Alumina website

Next.js App Router, TypeScript, and Tailwind with an ivory, charcoal/olive, and bronze editorial design. Custom SVG tarot artwork, mobile navigation, reflection card prompts, accessible FAQ accordion, and inline Cal.com scheduling via the official React embed.

```sh
npm ci
cp .env.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_CAL_BOOKING_URL` to the client-owned HTTPS Cal.com profile or event URL. An unset or invalid URL shows a coming-soon message. Customers can select sessions and appointments without leaving the site. No prices, durations, testimonials, or client biography are invented. Reflection cards show predefined journaling prompts, not generated readings or predictions. Copy needs client approval before launch.

Validation: `npm run lint`, `npm run typecheck`, `npm run build`. Production hosting is not provisioned. See root documentation for rollout, security, and commercial hosting considerations.
