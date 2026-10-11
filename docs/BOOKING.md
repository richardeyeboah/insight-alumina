# Cal.com booking integration

## Implemented integration: hosted event link
1. The client owns the Cal.com account and connects the calendar used for availability and conflict checking.
2. Create real event types with client-approved title, duration, location/conferencing, timezone, buffers, notice period, and cancellation/reschedule settings. Configure payment only if required and supported; no price is invented here.
3. Test the event URL independently, then set `NEXT_PUBLIC_CAL_BOOKING_URL=https://cal.com/<owner>/<event>` in `apps/web/.env.local` or production web environment settings.
4. Restart locally or redeploy after changes. The app validates HTTPS, the exact `cal.com` hostname, no embedded credentials, and an owner/event path. Invalid or missing configuration keeps booking unavailable.
5. Verify bookings from the deployed site in the client's calendar, including confirmation, reschedule, cancellation, timezone behavior, conflict checking, and payment/refund handling if enabled.

The CTA sends visitors to Cal.com in the same tab. The scheduling provider controls the booking form and confirmation. No API key, webhook, embed, payment processor, or booking database has been connected by this repository.

## Optional embed (future)
Generate an embed from the client's actual event sharing tools using the current official Cal.com instructions. Keep a normal booking link as fallback, use an accessible title/focus behavior, test small screens, and disclose third-party data handling. Assess script loading, consent requirements, and content-security policy before adding the embed. Avoid custom availability or booking UI until a clear need justifies API complexity.

## Later webhook integration
After phase 2 ingestion is implemented, configure a secret-protected HTTPS receiver for the booking lifecycle events actually needed. Use separate secrets and test events for staging. Verify signed raw payloads, persist before acknowledgement, handle duplicates/out-of-order events, and reconcile provider state. Never place a Cal API key or webhook secret in the web app's public environment.

Reference: [Cal.com API v2](https://cal.com/docs/api-reference/v2/introduction). Use the account's current event sharing and developer webhook settings to obtain provider-specific embed snippets and supported events; confirm plan eligibility before relying on them.
