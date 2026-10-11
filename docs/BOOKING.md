# Cal.com booking integration

## Implemented integration: inline booking embed
1. The client owns the Cal.com account and connects the calendar used for availability and conflict checking.
2. Create real event types with client-approved title, duration, location/conferencing, timezone, buffers, notice period, and cancellation/reschedule settings. Configure payment only if required and supported; no price is invented here.
3. Test the event URL independently, then set `NEXT_PUBLIC_CAL_BOOKING_URL=https://cal.com/<owner>/<event>` in `apps/web/.env.local` or production web environment settings.
4. Restart locally or redeploy after changes. The app validates HTTPS, the exact `cal.com` hostname, no embedded credentials, and a profile or event path. Invalid or missing configuration keeps booking unavailable.
5. Verify bookings from the deployed site in the client's calendar, including confirmation, reschedule, cancellation, timezone behavior, conflict checking, and payment/refund handling if enabled.

The booking section uses the official @calcom/embed-react inline embed. Visitors select a session, date/time, and enter booking details inside the website; Cal.com handles the scheduling form and confirmation. An external link is available only under the loading troubleshooting disclosure. The public embed does not need an API key. The optional backend receives signed webhook events after server deployment and Cal.com configuration; no payment processor is connected by this code.

## Embed operations
The inline embed is configured from the public profile or event URL. Keep a normal booking link as fallback, use an accessible title/focus behavior, test small screens, and disclose third-party data handling. Assess script loading, consent requirements, and content-security policy before adding the embed. Avoid custom availability or booking UI until a clear need justifies API complexity.

## Implemented webhook receiver
Deploy the Docker backend, then configure a secret-protected HTTPS receiver for the booking lifecycle events actually needed. Use separate secrets and test events for staging. Verify signed raw payloads, persist before acknowledgement, handle duplicates/out-of-order events, and manually reconcile provider state; automatic reconciliation remains future work. See [Docker deployment](DOCKER_DEPLOYMENT.md) for the endpoint, event allowlist, and required secret. Never place a Cal API key or webhook secret in the web app's public environment.

Reference: [Cal.com API v2](https://cal.com/docs/api-reference/v2/introduction). Use the account's current event sharing and developer webhook settings to obtain provider-specific embed snippets and supported events; confirm plan eligibility before relying on them.
